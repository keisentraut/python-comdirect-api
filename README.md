# python-comdirect-api

This is a Python implementation of the new [comdirect REST API](https://www.comdirect.de/cms/kontakt-zugaenge-api.html). This API can be used to interact with the German bank comdirect and view your balances and transactions. The technical specification of the API (in German) is found [here](https://kunde.comdirect.de/cms/media/comdirect_REST_API_Dokumentation.pdf).

Currently, this is only a proof of concept, but I plan to make it more useable and maybe turn it into a Python module.

# Contributing

Contributions are welcome.
Verify tests pass by running `tox`. Additionally, run `black .` in order to fix your formatting.

# Disclaimer

Use at own risk. I'm not responsible if you lock your account or lose all your money. 

# Prerequisites

This module needs the following packages. This will be checked before the start:  
json  
datetime  
requests  
uuid  
base64  
io  
PIL  
