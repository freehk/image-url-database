import os

from faunadb import query as q
from faunadb.client import FaunaClient

FAUNADB_SECRET = os.environ.get("FAUNADB_SERVER_SECRET")


def upload_to_fauna(data):
    client = FaunaClient(secret=FAUNADB_SECRET)

    client.query(q.create(
        q.collection("freehongkong-gallery"), {"data": data}
    ))


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
    # TODO this part is hacky, might break at some point.
    if "design material" in tags:
        tag = "design material"
    else:
        tag = "all"
    client = FaunaClient(secret=FAUNADB_SECRET)
    data = client.query(q.paginate(q.match(q.ref("indexes/tags_freehongkong-gallery"), tag)))['data']
    response = client.query(q.map_expr(
        lambda x: q.get(x),
        data
    ))

    hashes = [el['data']['phash'] for el in response]

    return set(hashes)
