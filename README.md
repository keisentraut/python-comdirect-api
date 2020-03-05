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

In order to test this, you currently need to do the following:

```
python setup.py sdist
pip install dist/comdirect_api-0.1.tar.gz
```

Then, run ```python bin/download_all_documents.py``` or something else in the ```bin/``` folder.

# Contributing

Contributions are very welcome. Please open a pull request.

# Disclaimer

Use at own risk. I'm not responsible if you lock your account (three wrong login attempts) or lose all your money. 

# Prerequisites

This module needs the following packages. This will be checked before the start:  

```
json  
datetime  
requests  
uuid  
pillow
```
