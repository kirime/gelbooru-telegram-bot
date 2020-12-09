from telegram import InlineQueryResultPhoto, InlineQueryResultGif, InlineQueryResultVideo, \
    InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackQueryHandler, CallbackContext
from telegram.error import BadRequest
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
    def run(updater: Updater):
        updater.start_polling()
        updater.idle()
elif mode == "prod":
    def run(updater: Updater):
        PORT = int(os.getenv("PORT", "8443"))
        HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook(f'https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}')
else:
    logger.error("No MODE specified!")
    sys.exit(1)


def pong(update: Update, context: CallbackContext):
    update.message.reply_text('Pong')


def start(update: Update, context: CallbackContext):
    update.message.reply_text('This bot does not respond to direct messages. \nUse @gbooru_bot inline syntax.')


def process_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()


def image_keyboard(image: dict) -> InlineKeyboardMarkup:
    ratings = {
        's': 'Safe',
        'q': 'Questionable',
        'e': 'Explicit',
    }

    buttons = [[InlineKeyboardButton(ratings.get(image['rating'], 'No rating'),
                                     callback_data=image['rating']),
                InlineKeyboardButton('\U0001F517',
                                     url=f'https://gelbooru.com/index.php?page=post&s=view&id={image["id"]}'),
                ]]
    return InlineKeyboardMarkup(buttons)


def gelbooru_images(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return

    offset = update.inline_query.offset
    pid = int(offset) if offset else 0

    results = []
    query = autocomplete(query)
    images = get_images(query, pid=pid)
    for image in images:
        try:
            if image['full_url'].endswith('.webm'):
                result = InlineQueryResultVideo(
                    type='video',
                    id=image['id'],
                    title=image['id'],
                    video_url=image['full_url'].replace('.webm', '.mp4'),
                    mime_type="video/mp4",
                    thumb_url=image['thumbnail_url'],
                    reply_markup=image_keyboard(image),
                )
            elif image['full_url'].endswith('.gif'):
                result = InlineQueryResultGif(
                    id=image['id'],
                    title=image['id'],
                    gif_url=image['full_url'],
                    thumb_url=image['thumbnail_url'],
                    gif_height=image['image_width'],
                    gif_width=image['image_height'],
                    reply_markup=image_keyboard(image),
                )
            else:
                result = InlineQueryResultPhoto(
                    id=image['id'],
                    title=image['id'],
                    photo_url=image['full_url'],
                    thumb_url=image['thumbnail_url'],
                    photo_height=image['image_height'],
                    photo_width=image['image_width'],
                    reply_markup=image_keyboard(image),
                )
            results.append(result)
        except Exception as e:
            logger.error(e)
    context.bot.answer_inline_query(update.inline_query.id, results, next_offset=str(pid + 1))


def error_callback(update, context):
    try:
        raise context.error
    except BadRequest:
        logger.error(context.error)


if __name__ == '__main__':
    logger.info("Starting bot")

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    gelbooru_handler = InlineQueryHandler(gelbooru_images)
    callback_handler = CallbackQueryHandler(process_callback)

    dispatcher.add_handler(CommandHandler('ping', pong))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(gelbooru_handler)
    dispatcher.add_handler(callback_handler)
    dispatcher.add_error_handler(error_callback)

    run(updater)
