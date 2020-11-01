# python-comdirect-api

This is a Python implementation of the new [comdirect REST API](https://www.comdirect.de/cms/kontakt-zugaenge-api.html). This API can be used to interact with the German bank comdirect and view your balances and transactions. The technical specification of the API (in German) is found [here](https://kunde.comdirect.de/cms/media/comdirect_REST_API_Dokumentation.pdf).

Currently, only parts of this comdirect API are implemented.
Parts which are already implemented and work:

- OAuth 2-factor login process (Photo-TAN, Push-TAN, SMS-TAN)
- DOCUMENTS 
- ACCOUNT (balances & transactions)

Still to do:

- QUOTE
- ORDER
- INSTRUMENT
- DEPOT

Most likely, I won't implement those soon, this has two reasons:

- comdirect does not provide test accounts for creating transactions, so I would have to test it on my actual private savings which is crazy.
- I don't want to write a trading bot, so I don't have a need for this.



# How to use this

This Python module is currently not yet on PyPi.
So in order to build it, you need to clone this repository and then package it yourself:

```
python setup.py sdist
pip install dist/comdirect_api-0.1.tar.gz
```

After installing it, you can run one of the scripts in the ```bin``` folder or write your own script.

```
$ python bin/get_account_balances.py 
Please enter Photo-TAN: 123456
Balance of Direct Access Savings-Plus Account (DE012345678901234567890): 0 EUR
Recent transactions:
  2019-09-11 2019-09-11 -3000.15 EUR TRANSFER
     Reference: I2219254G2705657/2
     RemittanceInfo: 01Uebertrag auf Girokonto 02End-to-End-Ref.: 03nicht angegeben 
     EndToEndReference: nicht angegeben


Balance of Checking Account (DE09876543210987654321): 1234.56 EUR
Recent transactions:
  2020-01-03 2020-01-03 -12.34 EUR DIRECT_DEBIT
     Reference: 5012345678901234/12345
     RemittanceInfo: 01Globus TS Forchheim//Forchheim/DE 022020-01-03T20:07:16 KFN 0 VJ 1234
     EndToEndReference: None
[... snip ...]
```

# Disclaimer

*Use at own risk. I'm not responsible if you lock your account or lose all your money.*


# Contributing

Contributions are very welcome. Please open a pull request.
Before you commit, run ```tox .``` in order to check for code style and to run the (not yet existing...) test cases.

## Dependencies 

This module needs the following packages. 

```
json
datetime
requests
uuid
base64
io
pillow
time
decimal
```
