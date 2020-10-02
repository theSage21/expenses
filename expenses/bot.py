import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from expenses import ops, const


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
