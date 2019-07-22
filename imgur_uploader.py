"""
This does not check for duplicates.
"""
import json
import os
from base64 import b64encode
from io import BytesIO

import imagehash
import requests
from PIL import Image

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


def calculate_hash(thumbnail):
    if HASH_TYPE == 'phash':
        return str(imagehash.phash(thumbnail))


def upload_to_imgur(image, image_type):
    # Dirty
    headers = {"Authorization": "Client-ID {}".format(CLIENT_ID)}
    if image_type == "base64":
        with open(image, 'rb') as image_file:
            binary_data = image_file.read()
            image = b64encode(binary_data)
            payload = {"image": image, "type": image_type}
    elif image_type == "url":
        payload = {"image": image, "type": image_type}
    else:
        raise Exception("Unexpected type")
    response = requests.post("https://api.imgur.com/3/image", params=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.content)


def write_result_to_json(images, output_path):
    with open(output_path, 'w') as outfile:
        json.dump(images, outfile)


def read_phashes(hashes_path):
    if os.path.isfile(hashes_path):
        with open(hashes_path) as infile:
            hashes = set(current_place.rstrip() for current_place in infile.readlines())
    else:
        hashes = set()
    return hashes


def write_hashes(existing_hashes, hashes_path):
    with open(hashes_path, 'w') as outfile:
        outfile.writelines("%s\n" % place for place in existing_hashes)
        outfile.writelines(existing_hashes)


def main(input_path, output_path, hashes_path, input_type):
    images = read_image_source(input_path)
    existing_hash = read_phashes(hashes_path)

    for image in images:
        thumbnail = create_thumbnail(image['url'])
        hash = calculate_hash(thumbnail)
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
    main(in_path, out_path, hashes, "links")
