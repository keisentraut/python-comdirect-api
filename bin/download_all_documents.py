#!/usr/bin/env python3
from comdirect_api.session import Session
from creds import user, password, client_id, client_secret
import os
import sys

# During development, you can store your credentials in bin/creds.py.
# Just put something like the following there:
#     user = "XXXXXXXX"
#     password = "XXXXXX"
#     client_id = "User_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#     client_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Alternatively, just hard-code them here.

# Define directory to store documents in (or leave emtpy)
# Alternatively, you can use a script parameter
if len(sys.argv) == 2:
    PATH = os.path.dirname(sys.argv[1])
else:
    print(f"usage: {sys.argv[0]} PATH")

# This downloads all documents (pagingcount defines the number of
# documents per page
pagingcount = 50

s = Session(user, password, client_id, client_secret)
pagingfirst = 0
hasmore = True

while hasmore:
    count = 0
    for d in s.documents_list(paging_count=pagingcount, paging_first=pagingfirst):
        count += 1
        filename = d.get_filename()
        print(f"downloading document {pagingfirst +count} {filename}...")
        content = s.documents_download(d)

        with open(os.path.join(PATH, filename), "wb") as f:
            f.write(content)
    hasmore = count == pagingcount
    if hasmore:
        print(f"fetching next page of documents {pagingfirst+pagingcount} to {pagingfirst+pagingcount*2}")
        pagingfirst += pagingcount
    else:
        print(f"finished fetching {pagingfirst + count} documents ")
