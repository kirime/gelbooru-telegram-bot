import requests
import json
import urllib.parse
from os.path import splitext, basename


def get_images(query, limit=50, pid=0):
    tags = urllib.parse.quote(query.strip())
    request_url = f'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&limit={limit}&pid={pid}&tags={tags}'

    response = requests.get(request_url)
    if response.status_code != 200:
        return []

    try:
        json_response = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        return []

    results = []
    for json_item in json_response:
        full_url = json_item['file_url']
        if json_item['sample']:
            full_url = get_sample_url(json_item['file_url'])
            height = json_item['sample_height']
            width = json_item['sample_width']
        else:
            height = json_item['height']
            width = json_item['width']

        extension = splitext(basename(full_url))[1]
        if extension not in ['.jpeg', '.jpg', '.gif', '.png']:
            continue

        result = dict()
        result['id'] = json_item['id']
        result['rating'] = json_item['rating']
        result['thumbnail_url'] = get_thumbnail_url(json_item['file_url'])
        result['full_url'] = full_url
        result['image_height'] = height
        result['image_width'] = width
        results.append(result)

    results = results[:50]
    return results


def get_thumbnail_url(full_url):
    prefix1, prefix2, image_name = full_url.split('/')[-3:]
    image_name = image_name.split('.')[0]
    return f'https://gelbooru.com/thumbnails/{prefix1}/{prefix2}/thumbnail_{image_name}.jpg'


def get_sample_url(full_url):
    prefix1, prefix2, image_name = full_url.split('/')[-3:]
    image_name = image_name.split('.')[0]
    return f'https://img2.gelbooru.com//samples/{prefix1}/{prefix2}/sample_{image_name}.jpg'


def autocomplete(query):
    split_query = query.rsplit(' ', 1)
    last_tag = split_query[-1]
    rest_of_query = split_query[0] if len(split_query) > 1 else ''

    if not last_tag:  # no need to make requests if last tag is empty
        return query

    encoded_last_tag = urllib.parse.quote(last_tag)
    request_url = f'https://gelbooru.com/index.php?page=autocomplete&term={encoded_last_tag}'
    response = requests.get(request_url)
    if response.status_code != 200:
        return query

    try:
        autocompleted_tag_list = list(json.loads(response.text))
        autocompleted_tag = autocompleted_tag_list[0]
    except (IndexError, json.decoder.JSONDecodeError):
        return query

    return ' '.join([rest_of_query, autocompleted_tag])
