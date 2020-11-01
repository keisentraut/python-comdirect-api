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

import datetime


def compress_duplicate_spaces(s):
    s = str(s)
    while "  " in s:
        s = s.replace("  ", " ")
    return s


# This shows the balances of your (first 1000) accounts
s = Session(user, password, client_id, client_secret)
for account_balance in s.account_get_balances():
    account = account_balance.account
    balance = account_balance.balance
    print(f"Balance of {account}: {balance}")
    accountId = account.accountId
    print("Recent transactions:")
    transactions = s.account_get_transactions(
        accountId,
        # TODO: comdirect has not implemented this.
        # see https://community.comdirect.de/t5/Website-Apps/Rest-API-Filter-Parameter/m-p/108710
        min_bookingdate=(datetime.date.today() - datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
        max_bookingdate=(datetime.date.today()).strftime("%Y-%m-%d"),
    )
    for t in transactions:
        if t.bookingDate is None:
            t.bookingDate = "XXXX-XX-XX"
        print(f"  {t.bookingDate} {t.valutaDate} {t.amount} {t.transactionType}\n"
              f"     Reference: {compress_duplicate_spaces(t.reference)}\n"
              f"     RemittanceInfo: {compress_duplicate_spaces(t.remittanceInfo)}\n"
              f"     EndToEndReference: {compress_duplicate_spaces(t.endToEndReference)}\n")
    print()

# This API call gets a single account balance, but you need to know the accountid in advance.
# So it's kinda useless in reality.
# print(s.account_get_balance(b.account.accountId))
