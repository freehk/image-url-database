# image-url-database
Python script to upload pictures to an image hosting service and save the urls in a database

## Plan
The current plan is to
1. create thumbnails of each image
1. calculate the phash for us to keep track of duplicates
1. upload the image and its thumbnail to a webservice (e.g. imgur) with tags via the API
1. save the resulting url and all the metadata in a json
1. send this to a database (e.g. faunadb) queryable by the website

## Data format
```
ID: int
phash: str
thumbnail_url: str
url: str
alt: str
description: str
tags: array
source: str
date_of_event: datetime
type: enum[image, video]
language: str
date_added: datetime
date_modified: datetime
```

with indices on phash, tags, and dates.