from telegram import InlineQueryResultPhoto
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from gelbooru import get_images
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
    results = list()
    images = get_images(query.split(' '), limit=10, page_id=0)
    for image in images:
        results.append(
            InlineQueryResultPhoto(
                id=query,
                title='Gelbooru images',
                photo_url=image['full_url'],
                thumb_url=image['thumbnail_url']
            )
        )
    bot.answer_inline_query(update.inline_query.id, results)


if __name__ == '__main__':
    logger.info("Starting bot")

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    gelbooru_handler = InlineQueryHandler(gelbooru_images)

    dispatcher.add_handler(CommandHandler('ping', pong))
    dispatcher.add_handler(gelbooru_handler)

    run(updater)