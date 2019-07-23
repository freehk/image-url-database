import datetime

import click
import json
import os
from io import BytesIO

import requests
from PIL import Image
from tqdm import tqdm

from utils import calculate_hash, read_phashes, write_result_to_json, write_hashes, upload_to_imgur, check_output_path

CLIENT_ID = os.environ.get("CLIENT_ID")
HASH_TYPE = "phash"
THUMBNAIL_SIZE = (150, 150)


def read_image_source(input_path):
    # TODO do something different if it's txt
    with open(input_path) as json_file:
        images = json.load(json_file)
    return images


def create_thumbnail(url):
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    im.thumbnail(THUMBNAIL_SIZE)
    im.save("thumbnail.jpg")
    return im


@click.command()
@click.option("--input_path", type=click.Path())
@click.option("--output_path", type=click.Path())
@click.option("--hashes_path", type=click.Path(), default="hashes.txt")
def main(input_path, output_path, hashes_path):
    if not output_path:
        output_path = str(datetime.datetime.now()) + '.json'
    images = read_image_source(input_path)
    existing_hash = read_phashes(hashes_path)
    check_output_path(output_path)
    result = []

    for image in tqdm(images):
        try:
            thumbnail = create_thumbnail(image['url'])
            hash = calculate_hash(thumbnail, HASH_TYPE)
            if hash in existing_hash:
                print("skipping a file")
            else:
                existing_hash.add(hash)
                write_hashes(existing_hash, hashes_path)  # TODO rewrite everything, should just append
                response_thumbnail = upload_to_imgur("thumbnail.jpg", image_type="base64", client_id=CLIENT_ID)
                response_image = upload_to_imgur(image['url'], image_type="url", client_id=CLIENT_ID)
                image.update(**{
                    HASH_TYPE: hash,
                    "response_thumbnail": response_thumbnail,
                    "response_image": response_image
                })
                result.append(image)
        except Exception as e:
            print(e)
    write_result_to_json(result, output_path)


if __name__ == '__main__':
    main()
