import requests
import json
import urllib.parse


def get_images(tags, limit=10, page_id=0):
    tags.append('rating:safe')
    tags.append('sort:score')

    params = {
        'page': 'dapi',
        's': 'post',
        'q': 'index',
        'json': 1,
        'limit': limit,
        'pid': page_id,
    }
    request_url = f'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&' \
        f'limit={params["limit"]}&pid={params["pid"]}&tags={urllib.parse.quote(" ".join(tags))}'

    response = requests.get(request_url)
    if response.status_code == 200:
        json_response = json.loads(response.text)
        results = [
            {
                'full_url': entry['file_url'],
                'thumbnail_url': get_thumbnail_url(entry['file_url'])
            }
            for entry in json_response]
        return results


def get_thumbnail_url(full_url):
    prefix1, prefix2, image_name = full_url.split('/')[-3:]
    image_name = image_name.split('.')[0]
    return f'https://gelbooru.com/thumbnails/{prefix1}/{prefix2}/thumbnail_{image_name}.jpg'
