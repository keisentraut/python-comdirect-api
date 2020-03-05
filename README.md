# python-comdirect-api

This is a Python implementation of the new [comdirect REST API](https://www.comdirect.de/cms/kontakt-zugaenge-api.html). This API can be used to interact with the German bank comdirect and view your balances and transactions. The technical specification of the API (in German) is found [here](https://kunde.comdirect.de/cms/media/comdirect_REST_API_Dokumentation.pdf).

Currently, only parts of this comdirect API are implemented.
Parts which are already implemented and work:

- OAuth 2-factor login process
- DOCUMENTS

Still to do:

- ACCOUNT
- QUOTE
- ORDER
- INSTRUMENT
- DEPOT


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
Balance of Direct Access Savings-Plus Account (DE08200411112345678901): 0 EUR
Balance of Checking Account (DE00200411112345678901): 1234.56 EUR
```

# Disclaimer

*Use at own risk. I'm not responsible if you lock your account or lose all your money.*



# Contributing

Contributions are very welcome. Please open a pull request.

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
