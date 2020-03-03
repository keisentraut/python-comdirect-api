#!/usr/bin/env python3

# During development, you can store your credentials in bin/creds.py.
# Just put something like the following there:
#     user = "XXXXXXXX"
#     password = "XXXXXX"
#     client_id = "User_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
#     client_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Alternatively, just hard-code them here.
from .creds import user, password, client_id, client_secret
from comdirect_api.session import Session

# getting your balance is now easy!
s = Session(user, password, client_id, client_secret)
print(s.account_get_balances())
