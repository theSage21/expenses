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
    else:
        text = "Something went wrong while recording the transaction."
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
        reply_to_message_id=update.message.id,
    )


def runbot():
    updater = Updater(token=const.TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    report_handler = CommandHandler("report", report)
    record_handler = MessageHandler(Filters.text & (~Filters.command), record)
    dispatcher.add_handler(report_handler)
    dispatcher.add_handler(record_handler)
    updater.start_polling()
