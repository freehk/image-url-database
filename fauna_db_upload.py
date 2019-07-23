import datetime
import json
import os

import click
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


def get_data_from_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
        formatted_data = [format_data(d) for d in data]
    return formatted_data


@click.command()
@click.option("--json_path", type=click.Path(exists=True))
def main(json_path):
    data = get_data_from_json(json_path)
    client = FaunaClient(secret=FAUNADB_SECRET)

    client.query(
        q.map_expr(
            lambda x: q.create(
                q.collection("freehongkong-gallery"),
                {"data": x}
            ),
            data))


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


if __name__ == '__main__':
    main()
