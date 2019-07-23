import json
import os
from base64 import b64encode

import imagehash
import requests


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


def calculate_hash(thumbnail, hash_type):
    if hash_type == 'phash':
        return str(imagehash.phash(thumbnail))


def upload_to_imgur(image, image_type, client_id):
    # Dirty
    headers = {"Authorization": "Client-ID {}".format(client_id)}
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


def check_output_path(output_path):
    if os.path.isfile(output_path):
        raise Exception("output_path already exists, please choose a different one to avoid overwriting")