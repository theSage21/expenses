import re
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from expenses import const, db


# Regexes to extract amounts from messages
AMOUNTS = [
    re.compile(s, re.DOTALL | re.IGNORECASE)
    for s in [r".*INR[^\d]*(\S+).*", r".*RS[^\d]*(\S+).*"]
]
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

TAGS = [
    (prefix, re.compile(s, re.DOTALL | re.IGNORECASE))
    for prefix, s in [
        ("bank", r".*(HDFC).*"),
        ("bank", r".*(ICICI).*"),
        ("bank", r".*(IPRUMF).*"),
        ("bank", r".*(SBI).*"),
        ("upi", r".*to\s+vpa\s+(\w+@\w+).*upi ref no.*"),
        ("dac", r".*from\s+a\/c\s+([\w\*]+)\s+on.*"),
        ("dac", r".*acct\s+(\w+)\s+debited\s+with\s+inr.*"),
        (
            "cac",
            r".*a\/c\s+no[\s\.]+(\w+)\s+is\s+credited\s+by.*",
        ),
        (
            "cac",
            r".*a\/c\s+(\w+)\s+credited\s.*",
        ),
        (
            "cac",
            r".*acct\s+(\w+)\s+has\s+been\s+credited\s+with.*",
        ),
        (
            "cac",
            r".*acct\s+(\w+)\s+credited.*",
        ),
        (
            "cac",
            r".*a\/c\s+(\w+)\s+credited.*",
        ),
        (
            "card",
            r".*via\s+debit\s+card\s+(\w+)\s+at.*",
        ),
        (
            "vendor",
            r".*via\s+debit\s+card\s+\w+\s+at\s+(\S+).*",
        ),
    ]
]


def parse(sms: str) -> (bool, int):
    amount = None
    for rgx in AMOUNTS:
        amount = rgx.match(sms)
        if amount:
            amount = amount.group(1)
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
            tags.add(f"{prefix}:{match.group(1)}")
    return tags


def record(update, context):
    msg = update.message.text
    is_expense, amount, is_parsed = False, None, False
    try:
        is_expense, amount = parse(msg)
        spent = "spent" if is_expense else "notSpent"
        text = f"{spent:>9}: {amount}."
        is_parsed = True
    except Exception as e:
        logging.exception(e)
        text = f"Unable to record."
    finally:
        tags = ""
        if is_expense:
            tags = tuple(sorted(tag_message(sms)))
            text += "\nTAGS\n" + " ".join(f"#{t}" for t in tags)
            tags = " ".join(Tags)
            tags = f" {tags} "
        with db.session() as session:
            session.add(
                db.Message(
                    sms=sms,
                    is_expense=is_expense,
                    amount=amount,
                    is_parsed=is_parsed,
                    tags=tags,
                )
            )
            session.commit()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.message.message_id,
    )


def report(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Not implemented yet.",
        reply_to_message_id=update.message.message_id,
    )


def runbot():
    updater = Updater(token=const.TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    record_handler = MessageHandler(Filters.text & (~Filters.command), record)
    dispatcher.add_handler(record_handler)
    updater.start_polling()
