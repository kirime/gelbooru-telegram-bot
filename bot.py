from telegram import InlineQueryResultPhoto
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from gelbooru import get_images, autocomplete
import logging
import os
import sys

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
if mode == "dev":
    def run(updater):
        updater.start_polling()
        updater.idle()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def pong(bot, update):
    update.message.reply_text('Pong')


def gelbooru_images(bot, update):
    query = update.inline_query.query
    if not query:
        return

    offset = update.inline_query.offset
    pid = int(offset) if offset else 0
    limit = 50

    results = []
    query = autocomplete(query)
    images = get_images(query, limit=limit, pid=pid)
    for image in images:
        try:
            results.append(
                InlineQueryResultPhoto(
                    id=image['id'],
                    title=image['id'],
                    photo_url=image['full_url'],
                    thumb_url=image['thumbnail_url'],
                    photo_height=image['photo_height'],
                    photo_width=image['photo_width'],
                )
            )
        except Exception as e:
            logger.error(e)
    bot.answer_inline_query(update.inline_query.id, results, next_offset=str(pid+1))


if __name__ == '__main__':
    logger.info("Starting bot")

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    gelbooru_handler = InlineQueryHandler(gelbooru_images)

    dispatcher.add_handler(CommandHandler('ping', pong))
    dispatcher.add_handler(gelbooru_handler)

    run(updater)
