#!/usr/bin/env python3

# During development, you can store your credentials in bin/creds.py.
# Just put something like the following there:
#     user = "XXXXXXXX"
#     password = "XXXXXX"
#     client_id = "User_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#     client_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Alternatively, just hard-code them here.
from creds import user, password, client_id, client_secret

from comdirect_api.session import Session


# This downloads all documents (actually, only the first 1000)
s = Session(user, password, client_id, client_secret)
for d in s.documents_list():
    filename = d.get_filename()
    print(f"downloading {filename}...")
    content = s.documents_download(d)
    with open(filename, "wb") as f:
        f.write(content)
