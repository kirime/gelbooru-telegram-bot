import requests
import json
import urllib.parse
from os.path import splitext, basename
from typing import List, Optional


def get_images(query: str, pid: int = 0, api_key: str = None, user_id: str = None) -> List[dict]:
    tags = urllib.parse.quote(query.strip())
    request_url = f'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit=50&pid={pid}&tags={tags}'
    if api_key and user_id:
        request_url += f'&api_key={api_key}&user_id={user_id}'

    response = requests.get(request_url)
    if response.status_code != 200:
        raise ConnectionError(f'Non-200 response from Gelbooru, got {response.status_code} instead')

    try:
        json_response = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        return []

    results = []
    if 'post' not in json_response:
        return results
    elif isinstance(json_response['post'], dict):
        json_response_images_data = [json_response['post']]
    else:
        json_response_images_data = json_response['post']

    for json_item in json_response_images_data:
        full_url = json_item['file_url'].replace('img3.', 'img1.')   # img3 seems to be faulty at the moment
        has_sample = json_item.get('sample') and json_item['sample'] != '0'
        is_video = full_url.endswith('.mp4') or full_url.endswith('.webm')
        if has_sample and not is_video:
            full_url = get_sample_url(json_item['file_url'])
            height = json_item['sample_height']
            width = json_item['sample_width']
        else:
            height = json_item['height']
            width = json_item['width']

        extension = splitext(basename(full_url))[1]
        if extension not in ['.jpeg', '.jpg', '.gif', '.png', '.webm', '.mp4']:
            continue

        result = dict()
        result['id'] = json_item['id']
        result['page_url'] = get_page_url_from_image_id(json_item['id'])
        result['rating'] = json_item['rating']
        result['thumbnail_url'] = get_thumbnail_url(json_item['file_url'])
        result['full_url'] = full_url
        result['image_height'] = height
        result['image_width'] = width
        results.append(result)
    return results


def get_thumbnail_url(full_url: str) -> str:
    prefix1, prefix2, image_name = full_url.split('/')[-3:]
    image_name = image_name.split('.')[0]
    return f'https://gelbooru.com/thumbnails/{prefix1}/{prefix2}/thumbnail_{image_name}.jpg'


def get_sample_url(full_url: str) -> str:
    prefix1, prefix2, image_name = full_url.split('/')[-3:]
    image_name = image_name.split('.')[0]
    return f'https://img1.gelbooru.com//samples/{prefix1}/{prefix2}/sample_{image_name}.jpg'


def get_page_url_from_image_id(image_id: int) -> str:
    return f'https://gelbooru.com/index.php?page=post&s=view&id={str(image_id)}'


def autocomplete(query: str) -> Optional[str]:
    """ Autocomplete last word in query to the most popular Gelbooru tag that starts with this word.
        Do nothing if the word is already a valid Gelbooru tag. """
    split_query = query.rsplit(' ', 1)
    last_tag = split_query[-1]
    rest_of_query = split_query[0] if len(split_query) > 1 else ''

    if not last_tag or last_tag.startswith(('-', '*', '~')) or last_tag.endswith('~') or ':' in last_tag:
        return query

    encoded_last_tag = urllib.parse.quote(last_tag)
    request_url = f'https://gelbooru.com/index.php?page=autocomplete2&term={encoded_last_tag}&limit=10'
    response = requests.get(request_url)
    if response.status_code != 200:
        raise ConnectionError(f'Non-200 response from Gelbooru, got {response.status_code} instead')

    try:
        autocompleted_tag_list = list(tag['value'] for tag in json.loads(response.text))
        # Do not autocomplete last word if it is already a valid tag
        if last_tag in autocompleted_tag_list:
            autocompleted_tag = last_tag
        else:
            autocompleted_tag = autocompleted_tag_list[0]
    except (IndexError, KeyError, json.decoder.JSONDecodeError):
        return None

    if rest_of_query:
        return f'{rest_of_query} {autocompleted_tag}'
    else:
        return autocompleted_tag
