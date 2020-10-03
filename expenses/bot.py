import re
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from expenses import ops, const
from . import db


# Possible formats in which the amount could be expressed
AMOUNTS = [
    re.compile(s)
    for s in [r".*INR[^\d]*(\S+).*" r".*Rs[^\d]*(\S+).*", r".*RS[^\d]*(\S+).*"]
]


def add_expense(sms):
    amount = None
    for rgx in AMOUNTS:
        amount = rgx.match(sms)
        if amount:
            break
    with db.session() as session:
        if amount is None:
            msg = db.Message(sms=sms)
        else:
            msg = db.Message(
                amount=amount.group(1), sms=sms, is_parsed=True, is_expense=False
            )
        session.add(msg)
        session.commit()


def record(update, context):
    msg = update.message.text
    text = "Recorded transaction."
    try:
        ops.add_expense(msg)
    except Exception as e:
        logging.exception(e)
        text = f"Seen transaction. Unable to record."
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_to_message_id=update.message.message_id,
    )


def report(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Not implemented",
        reply_to_message_id=update.message.message_id,
    )


def runbot():
    updater = Updater(token=const.TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    record_handler = MessageHandler(Filters.text & (~Filters.command), record)
    dispatcher.add_handler(record_handler)
    updater.start_polling()
