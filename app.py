import datetime
import logging

import pytz
from tqdm import tqdm

from utils.faunadb_utils import query_fauna_for_hashes, upload_to_fauna
from utils.imgur import query_imgur_by_tags, create_thumbnail, calculate_hash, upload_to_imgur

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    logger.info("querying imgur for tags: {}".format(tags))
    response = query_imgur_by_tags(tags)
    images = format_response(response)
    total_num = len(images)
    logger.info("{} images found".format(total_num))

    logger.info("querying fauna for hashes")
    existing_hashes = query_fauna_for_hashes(tags)
    logger.info("{} existing hashes found".format(len(existing_hashes)))

    logger.info("starting sync process")
    skipped = 0
    for image in tqdm(images):
        thumbnail = create_thumbnail(image['url'])
        phash = calculate_hash(thumbnail, "phash")
        if phash in existing_hashes:
            skipped += 1
            continue
        response_thumbnail = upload_to_imgur("thumbnail.jpg", image_type="base64")
        formatted_fauna_data = format_fauna(response_thumbnail, image, phash)
        upload_to_fauna(formatted_fauna_data)
        existing_hashes.add(phash)
    logger.info(
        "sync process completed, {} uploaded, {} skipped because of duplicates\n".format(total_num - skipped, skipped))


if __name__ == '__main__':
    sync_by_tags(["design material"])
    sync_by_tags([])
