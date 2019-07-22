"""
This does not check for duplicates.
"""
import json
import os

import requests

CLIENT_ID = os.environ.get("CLIENT_ID")
HASH_TYPE = "phash"


def read_image_source(input_path):
    with open(input_path) as json_file:
        images = json.load(json_file)
    return images


def create_thumbnail(image):
    return image


def calculate_hash(thumbnail):
    return "GAGWEG1241"


def upload_to_imgur(image, type):
    headers = {"Authorization": "Client_ID {}".format(CLIENT_ID)}
    payload = {"image": image, "type": type}
    response = requests.post("https://api.imgur.com/3/image", json=payload, headers=headers)
    return response


def write_result_to_json(images, output_path):
    with open(output_path, 'w') as outfile:
        json.dump(images, outfile)


def read_phashes(hashes_path):
    if os.path.isfile(hashes_path):
        with open(hashes_path) as infile:
            hashes = set(infile.readlines())
    else:
        hashes = set()
    return hashes


def write_hashes(existing_hashes, hashes_path):
    with open(hashes_path, 'w') as outfile:
        outfile.writelines(existing_hashes)


def main(input_path, output_path, hashes_path):
    images = read_image_source(input_path)
    existing_hash = read_phashes(hashes_path)

    for image in images:
        thumbnail = create_thumbnail(image['url'])
        hash = calculate_hash(thumbnail)
        if hash not in existing_hash:
            existing_hash.add(hash)
            response_thumbnail = upload_to_imgur(thumbnail, type="binary")  # TODO check type
            response_image = upload_to_imgur(image, type="url")
            image.update(**{HASH_TYPE: hash,
                            "response_thumbnail": response_thumbnail,
                            "response_image": response_image})

    write_result_to_json(images, output_path)
    write_hashes(existing_hash, hashes_path)


if __name__ == '__main__':
    hashes = "hashes.txt"
    in_path = "sample_input.json"
    out_path = "sample_output.json"
    main(in_path, out_path, hashes)
