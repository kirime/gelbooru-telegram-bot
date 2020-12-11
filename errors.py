from telegram import InputTextMessageContent, InlineQueryResultArticle

connection_error_message = InputTextMessageContent(message_text='Network error.')
connection_error_response = InlineQueryResultArticle(
    id='networkerror', title='No response from Gelbooru',
    description='Please try again a little later.',
    input_message_content=connection_error_message)

value_error_message = InputTextMessageContent(message_text='No results found with those tags.')
value_error_response = InlineQueryResultArticle(
    id='noresults', title='No results found',
    description='Please try different tags.',
    input_message_content=value_error_message)
