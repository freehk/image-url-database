# image-url-database
Python cron service to search imgur albums by tags, create thumbnail and post to imgur and save the urls in faunadb.

NEEDS some serious refactoring at some point. Code is all over the place.  

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
export CLIENT_ID={{your imgur client id}}
export FAUNADB_SERVER_SECRET={{your faunadb server secret}}
```