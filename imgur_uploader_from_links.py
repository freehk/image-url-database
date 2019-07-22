"""
This does not check for duplicates.
"""
import json
import os
from io import BytesIO

import requests
from PIL import Image

from utils import calculate_hash, read_phashes, write_result_to_json, write_hashes, upload_to_imgur

CLIENT_ID = os.environ.get("CLIENT_ID")
HASH_TYPE = "phash"
THUMBNAIL_SIZE = (120, 120)


def read_image_source(input_path):
    with open(input_path) as json_file:
        images = json.load(json_file)
    return images


def create_thumbnail(url):
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    im.thumbnail(THUMBNAIL_SIZE)
    im.save("thumbnail.jpg")
    return im


def main(input_path, output_path, hashes_path):
    images = read_image_source(input_path)
    existing_hash = read_phashes(hashes_path)

    for image in images:
        thumbnail = create_thumbnail(image['url'])
        hash = calculate_hash(thumbnail, HASH_TYPE)
        if hash not in existing_hash:
            existing_hash.add(hash)
            response_thumbnail = upload_to_imgur("thumbnail.jpg", image_type="base64")
            response_image = upload_to_imgur(image['url'], image_type="url")
            image.update(**{
                HASH_TYPE: hash,
                "response_thumbnail": response_thumbnail,
                "response_image": response_image
            })

    write_result_to_json(images, output_path)
    write_hashes(existing_hash, hashes_path)


if __name__ == '__main__':
    hashes = "hashes.txt"
    in_path = "sample_input.json"
    out_path = "sample_output.json"
    main(in_path, out_path, hashes)
