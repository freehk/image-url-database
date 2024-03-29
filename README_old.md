# image-url-database
Python script to upload pictures to an image hosting service and save the urls in a database

## Plan
The current plan is to
1. create thumbnails of each image
1. calculate the phash for us to keep track of duplicates
1. upload the image and its thumbnail to a webservice (e.g. imgur) with tags via the API
1. save the resulting url and all the metadata in a json
1. send this to a database (e.g. faunadb) queryable by the website

## Data schema
```
phash: str
thumbnail_url: str
url: str
alt: str
description: str
tags: array
source_url: str
date_of_event: datetime
type: enum[image, video]
language: str
date_added: datetime
date_modified: datetime
```

with indices on phash, tags, and dates.

## Environment
```bash
conda env create -f environment.yml
```

## How to upload a json of urls to imgur
```commandline
export CLIENT_ID={{your imgur client id}}
python imgur_upload_from_links.py --input_path sample_input.json --output_path out.json --hashes_path new_hashes.txt
```
You should see your output in `out.json` and the hashes in `new_hashes.txt`. Omit output_path and the generated json would be based on datetime

The hashes prevent you from uploading to imgur again. 

And... because it's written in a hurry, there will be a stray `thumbnail.jpg` lying in your dir after running. 

## How to upload that output json to faunadb
```commandline
export FAUNADB_SERVER_SECRET={{your faunadb server secret}}
python fauna_db_upload.py --json_path sample_output.json
```
you should see the data in the fauna dashboard