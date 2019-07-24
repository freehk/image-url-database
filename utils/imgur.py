import os
from base64 import b64encode
from io import BytesIO

import imagehash
import requests
from PIL import Image

CLIENT_ID = os.environ.get("CLIENT_ID")
HEADERS = {"Authorization": "Client-ID {}".format(CLIENT_ID)}
HASH_TYPE = "phash"
THUMBNAIL_SIZE = (150, 150)


def calculate_hash(thumbnail, hash_type):
    if hash_type == 'phash':
        return str(imagehash.phash(thumbnail))


def query_imgur_by_tags(tags):
    # TODO will need to paginate at some point
    response = requests.get("https://api.imgur.com/3/gallery/search",
                            params={"q": " AND ".join(tags)},
                            headers=HEADERS)
    response.raise_for_status()
    return response.json()


def upload_to_imgur(image, image_type):
    # Dirty
    if image_type == "base64":
        with open(image, 'rb') as image_file:
            binary_data = image_file.read()
            image = b64encode(binary_data)
            payload = {"image": image, "type": image_type}
    elif image_type == "url":
        payload = {"image": image, "type": image_type}
    else:
        raise Exception("Unexpected type")
    response = requests.post("https://api.imgur.com/3/image", data=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def create_thumbnail(url):
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    im.thumbnail(THUMBNAIL_SIZE)
    try:
        im.save("thumbnail.jpg")
    except:
        im = im.convert("RGB")
        im.save("thumbnail.jpg")
    return im
