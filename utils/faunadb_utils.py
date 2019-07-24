import datetime
import os

import pytz
from faunadb import query as q
from faunadb.client import FaunaClient

FAUNADB_SECRET = os.environ.get("FAUNADB_SERVER_SECRET")


def format_data(data):
    return {
        "phash": data['phash'],
        "thumbnail_url": data['response_thumbnail']['data']['link'],
        "url": data['response_image']['data']['link'],
        "source_url": data['url'],
        "tags": ['all'],
        "date_added": pytz.utc.localize(datetime.datetime.utcnow()),
        "date_modified": pytz.utc.localize(datetime.datetime.utcnow())
    }


def upload_to_fauna(query):
    client = FaunaClient(secret=FAUNADB_SECRET)

    client.query(
        q.map_expr(
            lambda x: q.create(
                q.collection("freehongkong-gallery"),
                {"data": x}
            ),
            query))


def update_tags():
    client = FaunaClient(secret=FAUNADB_SECRET)
    response = client.query(q.paginate(q.difference(q.match(q.ref("indexes/tags_freehongkong-gallery"), "all"),
                                                    q.match(q.ref("indexes/tags_freehongkong-gallery"),
                                                            "design material"))))

    client.query(
        q.map_expr(
            lambda x: q.update(
                x,
                {"data": {"tags": ["all", "photo"]}}
            ),
            response['data']
        )
    )


def query_fauna_for_hashes(tags):
    if "design material" in tags:
        tag = "design material"
    else:
        tag = "photo"
    client = FaunaClient(secret=FAUNADB_SECRET)
    data = client.query(q.paginate(q.match(q.ref("indexes/tags_freehongkong-gallery"), tag)))['data']
    response = client.query(q.map_expr(
        lambda x: q.get(x),
        data
    ))

    hashes = [el['data']['phash'] for el in response]

    return set(hashes)
