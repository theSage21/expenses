import re
import calendar
import logging
from collections import namedtuple
import sqlalchemy as sa
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from expenses import const, db


# Regexes to extract amounts from messages
AMOUNTS = [
    re.compile(s, re.DOTALL | re.IGNORECASE)
    for s in [r"INR[\s\.\:]*([\d,]+\.?[\d]+)", r"RS[\s\.\:]*([\d,]+\.?[\d]+)"]
]
INR, RS = AMOUNTS
# Record only these patterns as expenses so that we don't accidentally mark
# spam smses as valid expenses.
EXPENSES = [
    re.compile(s, re.DOTALL | re.IGNORECASE)
    for s in [
        r".*your acct [x\d]+ has been credited with inr.*the avbl bal is.*",
        r".*your a\/c [x\d]+ credited inr.*bal.*",
        r".*your a\/c no\. [x\d]+ is credited.*linked to mobile.*",
        r".*acct [x\d\*]+ debited with inr [\d\.,]+.*imps",
        r".*rs[\.\s]*[\d\.,]+ debited from.*vpa.*upi ref no.*",
        r".*via debit card [\dx]+ at.*",
        r".*sip purchase of rs[\d\.,]+ in folio.*",
        r".*your sip purchase in folio.*under hdfc",
    ]
]

# Extract information from messages and add them to the tags field. This will
# allow for easier grouping and categorization.
TAG = namedtuple("TAG", "BANK UPI DEBIT_ACCOUNT CREDIT_ACCOUNT CARD VENDOR")(
    "bank", "upi", "dac", "cac", "card", "vendor"
)


TAGS = [
    (prefix, re.compile(s, re.DOTALL | re.IGNORECASE))
    for prefix, s in [
        (TAG.BANK, r".*(HDFC).*"),
        (TAG.BANK, r".*(ICICI).*"),
        (TAG.BANK, r".*(IPRUMF).*"),
        (TAG.BANK, r".*(SBI).*"),
        (TAG.UPI, r".*to\s+vpa\s+(\w+@\w+).*upi ref no.*"),
        (TAG.DEBIT_ACCOUNT, r".*from\s+a\/c\s+([\w\*]+)\s+on.*"),
        (TAG.DEBIT_ACCOUNT, r".*acct\s+(\w+)\s+debited\s+with\s+inr.*"),
        (
            TAG.CREDIT_ACCOUNT,
            r".*a\/c\s+no[\s\.]+(\w+)\s+is\s+credited\s+by.*",
        ),
        (
            TAG.CREDIT_ACCOUNT,
            r".*a\/c\s+(\w+)\s+credited\s.*",
        ),
        (
            TAG.CREDIT_ACCOUNT,
            r".*acct\s+(\w+)\s+has\s+been\s+credited\s+with.*",
        ),
        (
            TAG.CREDIT_ACCOUNT,
            r".*acct\s+(\w+)\s+credited.*",
        ),
        (
            TAG.CREDIT_ACCOUNT,
            r".*a\/c\s+(\w+)\s+credited.*",
        ),
        (
            TAG.CARD,
            r".*via\s+debit\s+card\s+(\w+)\s+at.*",
        ),
        (
            TAG.VENDOR,
            r".*via\s+debit\s+card\s+\w+\s+at\s+(.+)\s+on.*",
        ),
    ]
]


def parse(sms: str) -> (bool, int):
    amount = None
    for rgx in AMOUNTS:
        amount = rgx.findall(sms) or None
        if amount:
            # The first amount is usually the actual amount
            amount = amount[0]
            break
    is_expense = False
    _sms = " ".join(sms.lower().split())
    for rgx in EXPENSES:
        match = rgx.match(_sms)
        if match:
            is_expense = True
            break
    return is_expense, amount


def tag_message(sms: str) -> set:
    tags = set()
    for prefix, rgx in TAGS:
        match = rgx.match(sms)
        if match:
            tags.add(f"{prefix}.{match.group(1).strip()}")
    return tags


def record(update, context):
    sms = update.message.text
    is_expense, amount, is_parsed, is_debit = False, None, False, False
    tags = ""
    try:
        is_expense, amount = parse(sms)
        if is_expense:
            tags = tuple(sorted(tag_message(sms)))
            if any(t.startswith(TAGS.DEBIT_ACCOUNT) for t in tags):
                is_debit = True
            tags = " ".join(tags)
            tags = f" {tags} "
        spent = "spent" if is_debit else "notSpent"
        text = f"{spent:>9}: {amount or 'anything'}."
        is_parsed = True
    except Exception as e:  # pylint: disable=broad-except
        logging.exception(e)
        text = "Unable to record."
    finally:
        with db.session() as session:
            session.add(  # pylint: disable=no-member
                db.Message(
                    sms=sms,
                    is_expense=is_debit,
                    amount=amount,
                    is_parsed=is_parsed,
                    tags=tags,
                )
            )
            session.commit()  # pylint: disable=no-member
    update.message.delete()
    if is_expense:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"{sms}\n===============\n{text}"
        )


def humanize(amt):
    if amt < 1000:
        return f"{amt:<6}"
    if amt < 1_00_000:
        d = amt / 1000
        d = round(d, 2)
        d = int(d) if d == int(d) else d
        d = f"{d}K"
        return f"{d:<6}"
    d = amt / 1_00_000
    d = round(d, 2)
    d = int(d) if d == int(d) else d
    d = f"{d}L"
    return f"{d:<6}"


def monthly_report():
    last_5_months = (
        db.utcnow().subtract(months=5).set(day=1, hour=0, minute=0, second=0)
    )
    rows = []
    with db.session() as session:
        for row in (
            session.query(db.Message)  # pylint: disable=no-member
            .filter(
                db.Message.is_expense == True,  # pylint: disable=singleton-comparison
                db.Message.amount.isnot(None),
                db.Message.created_at >= last_5_months,
            )
            .group_by(sa.func.extract("month", db.Message.created_at))
            .order_by(db.Message.created_at.desc())
            .with_entities(
                sa.func.extract("month", db.Message.created_at),
                sa.func.sum(db.Message.amount),
            )
        ):
            rows.append((calendar.month_name[row[0]][:3], row[1]))
    return rows


def weekly_report():
    last_5_weeks = db.utcnow().subtract(days=5 * 7).set(hour=0, minute=0, second=0)
    rows = []
    with db.session() as session:
        for row in (
            session.query(db.Message)  # pylint: disable=no-member
            .filter(
                db.Message.is_expense == True,  # pylint: disable=singleton-comparison
                db.Message.amount.isnot(None),
                db.Message.created_at >= last_5_weeks,
            )
            .group_by(sa.func.extract("week", db.Message.created_at))
            .order_by(db.Message.created_at.desc())
            .with_entities(
                sa.func.extract("week", db.Message.created_at),
                sa.func.sum(db.Message.amount),
            )
        ):
            rows.append((row[0], row[1]))
    this_week = max([w for w, _ in rows])
    rows = [
        (f"{w - this_week} week" if w != this_week else "This week", total)
        for w, total in rows
    ]
    return rows


def make_reporter(row_builder):
    def send_report(update, context):
        rows = row_builder()
        report = "\n".join(
            f"{period}: {humanize(total)} ({total})" for period, total in rows
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"```\n{report}\n```",
            parse_mode="Markdown",
            reply_to_message_id=update.message.message_id,
        )

    return send_report


def runbot():
    updater = Updater(token=const.TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    record_handler = MessageHandler(Filters.text & (~Filters.command), record)
    dispatcher.add_handler(record_handler)
    dispatcher.add_handler(CommandHandler("monthly", make_reporter(monthly_report)))
    dispatcher.add_handler(CommandHandler("weekly", make_reporter(weekly_report)))
    updater.start_polling()
