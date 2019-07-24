import datetime

import pytz

from utils.faunadb_utils import query_fauna_for_hashes, upload_to_fauna
from utils.imgur import query_imgur_by_tags, create_thumbnail, calculate_hash, upload_to_imgur


def format_response(response):
    images = []
    for album in response['data']:
        album_tags = [tag.get('display_name') for tag in album.get('tags', {})]
        album_title = album.get('title')
        album_description = album.get('description')
        album_link = album.get('link')
        for image in album['images']:
            image_title = image.get('title')
            image_description = image.get('description')
            image_tags = [tag.get('display_name') for tag in image.get('tags', {})]
            image_timestamp = image['datetime']
            image_link = image['link']
            images.append({
                "url": image_link,
                "tags": ['all'] + album_tags + image_tags,
                "description": image_description or album_description,
                "alt": image_title or album_title,
                "date_added": pytz.utc.localize(datetime.datetime.fromtimestamp(image_timestamp)),
            })

    return images


def format_fauna(response_thumbnail, image, phash):
    result = {**image, **{"thumbnail_url": response_thumbnail['data']['link'], "phash": phash}}
    return result


def sync_by_tags(tags):
    tags = set(["freehongkong"] + tags)
    response = query_imgur_by_tags(tags)
    images = format_response(response)
    existing_hashes = query_fauna_for_hashes(tags)
    for image in images:
        thumbnail = create_thumbnail(image['url'])
        phash = calculate_hash(thumbnail, "phash")
        if phash in existing_hashes:
            continue
        response_thumbnail = upload_to_imgur("thumbnail.jpg", image_type="base64")
        formatted_query = format_fauna(response_thumbnail, image, phash)
        upload_to_fauna(formatted_query)
        existing_hashes.add(phash)


if __name__ == '__main__':
    sync_by_tags(["design material"])
    sync_by_tags([])
