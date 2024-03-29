from telegram import InlineQueryResultPhoto, InlineQueryResultGif, InlineQueryResultVideo, \
    InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, InlineQueryHandler, CallbackQueryHandler, CallbackContext
from telegram.error import BadRequest
from gelbooru import get_images, autocomplete
from errors import connection_error_response, no_results_error_response, autocomplete_error_response
import logging
import sys
import settings

# Enabling logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)

# Getting mode, so we could define run function for local and server setup
if settings.MODE == 'dev':
    def run(updater: Updater):
        updater.start_polling()
        updater.idle()
elif settings.MODE == 'prod':
    def run(updater: Updater):
        updater.start_webhook(listen='0.0.0.0',
                              port=settings.PORT,
                              url_path=settings.TOKEN,
                              webhook_url=f'{settings.WEBHOOK_PATH}/{settings.TOKEN}')
        updater.idle()
else:
    logger.error('No MODE specified!')
    sys.exit(1)


def pong(update: Update, context: CallbackContext):
    update.message.reply_text('Pong')


def start(update: Update, context: CallbackContext):
    update.message.reply_text('This bot does not respond to direct messages. \nUse @gbooru_bot inline syntax.')


def process_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()


def image_keyboard(image: dict, query: str) -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(str(image['rating']).capitalize(),
                                     callback_data=image['rating']),
                InlineKeyboardButton('\U0001F517',  # link symbol
                                     url=f'https://gelbooru.com/index.php?page=post&s=view&id={image["id"]}'),
                InlineKeyboardButton('\U0001F504',  # redo symbol
                                     switch_inline_query_current_chat=query),
                ]]
    return InlineKeyboardMarkup(buttons)


def gelbooru_images(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return

    logger.info(f'{update.inline_query.from_user.username} {update.inline_query.from_user.first_name} '
                f'{update.inline_query.from_user.last_name}: query : {query}')

    offset = update.inline_query.offset
    pid = int(offset) if offset else 0

    query = autocomplete(query)
    if query is None:
        context.bot.answer_inline_query(update.inline_query.id, [autocomplete_error_response])
        return

    results = []
    images = get_images(query, pid=pid, api_key=settings.API_KEY, user_id=settings.USER_ID)
    if pid == 0 and not images:
        context.bot.answer_inline_query(update.inline_query.id, [no_results_error_response])
        return

    for image in images:
        try:
            if image['full_url'].endswith('.webm') or image['full_url'].endswith('.mp4'):
                result = InlineQueryResultVideo(
                    type='video',
                    id=image['id'],
                    title=f'Video {image["image_width"]}×{image["image_height"]}',
                    video_url=image['full_url'],
                    mime_type='video/mp4',
                    thumb_url=image['thumbnail_url'],
                    reply_markup=image_keyboard(image=image, query=query),
                )
            elif image['full_url'].endswith('.gif'):
                result = InlineQueryResultGif(
                    id=image['id'],
                    title=image['id'],
                    gif_url=image['full_url'],
                    thumb_url=image['thumbnail_url'],
                    gif_height=image['image_height'],
                    gif_width=image['image_width'],
                    reply_markup=image_keyboard(image=image, query=query),
                )
            else:
                result = InlineQueryResultPhoto(
                    id=image['id'],
                    title=image['id'],
                    photo_url=image['full_url'],
                    thumb_url=image['thumbnail_url'],
                    photo_height=image['image_height'],
                    photo_width=image['image_width'],
                    reply_markup=image_keyboard(image=image, query=query),
                )
            results.append(result)
        except Exception as e:
            logger.error(e)
    context.bot.answer_inline_query(update.inline_query.id, results, next_offset=str(pid + 1))


def error_callback(update, context):
    try:
        raise context.error
    except (OSError, ConnectionError):
        logger.error(context.error)
        context.bot.answer_inline_query(update.inline_query.id, [connection_error_response])
    except BadRequest:
        logger.error(context.error)


if __name__ == '__main__':
    logger.info('Starting bot')

    request_kwargs = {
        'connect_timeout': settings.CONNECT_TIMEOUT,
        'read_timeout': settings.READ_TIMEOUT,
    }

    updater = Updater(token=settings.TOKEN, request_kwargs=request_kwargs)
    dispatcher = updater.dispatcher
    gelbooru_handler = InlineQueryHandler(gelbooru_images)
    callback_handler = CallbackQueryHandler(process_callback)

    dispatcher.add_handler(CommandHandler('ping', pong))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(gelbooru_handler)
    dispatcher.add_handler(callback_handler)
    dispatcher.add_error_handler(error_callback)

    run(updater)
