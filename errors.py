from telegram import InputTextMessageContent, InlineQueryResultArticle

connection_error_message = InputTextMessageContent(message_text='Network error.')
connection_error_response = InlineQueryResultArticle(
    id='networkerror', title='No response from Gelbooru',
    description='Please try again a little later.',
    input_message_content=connection_error_message)

no_results_error_message = InputTextMessageContent(message_text='No results found with those tags.')
no_results_error_response = InlineQueryResultArticle(
    id='noresults', title='No results found',
    description='Please try different tags.',
    input_message_content=no_results_error_message)

autocomplete_error_message = InputTextMessageContent(message_text='Could not find provided tags.')
autocomplete_error_response = InlineQueryResultArticle(
    id='notags', title='Could not autocomplete last tag',
    description='Gelbooru tag list does not contain any match.\nPlease fix a typo or try a different tag.',
    input_message_content=autocomplete_error_message)
