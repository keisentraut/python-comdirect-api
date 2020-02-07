#!/usr/bin/python
#
# Python script for interacting with comdirect REST API
#
# Copyright (C) 2020 Klaus Eisentraut
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import uuid
import datetime
import base64
import io 
import json
from PIL import Image

client_id="User_01234567890123456789012345678901"
client_secret="01234567890123456789012345678901"
username = "23456789"
password = "123456"


def currenttime():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")


response = requests.post(
        "https://api.comdirect.de/oauth/token", 
        data = """client_id=%s&client_secret=%s&username=%s&password=%s&grant_type=password""" % (client_id, client_secret, username, password),
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/x-www-form-urlencoded"
        }
)
tmp = response.json()
access_token = tmp["access_token"]
refresh_token = tmp["refresh_token"]
print("got response: " + str(tmp))

# GET /session/clients/user/v1/sessions
session_id = uuid.uuid4() 
response = requests.get(
    "https://api.comdirect.de/api/session/clients/user/v1/sessions", 
    allow_redirects=False, 
    headers = {
        "Accept":"application/json",
        "Authorization":"Bearer "+access_token,
        "x-http-request-info":"{\"clientRequestId\":{\"sessionId\":\"%s\",\"requestId\":\"%s\"}}" % (session_id, currenttime())
    }
)
print("got response: " + str(response.text))
tmp = response.json()
session_id = tmp[0]["identifier"] 
print("session_id = " + session_id)

#POST /session/clients/user/v1/sessions/{sessionId}/validate
response = requests.post(
        "https://api.comdirect.de/api/session/clients/user/v1/sessions/%s/validate" % session_id,
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Authorization":"Bearer "+access_token,
            "x-http-request-info":"{\"clientRequestId\":{\"sessionId\":\"%s\",\"requestId\":\"%s\"}}" % (session_id, currenttime()),
            "Content-Type":"application/json",
        },
        data='{"identifier":"%s","sessionTanActive":true,"activated2FA":true}' % session_id,
)
print("got response: " + str(response.headers["x-once-authentication-info"]))
tmp = json.loads(response.headers["x-once-authentication-info"])
challenge_id = tmp["id"]
challenge = tmp["challenge"]

# ask user for TAN
# TODO: I just assumed here it would be a Photo-TAN .
Image.open(io.BytesIO(base64.b64decode(challenge))).show()
challenge_tan = input("Please enter Photo-TAN: ")

# PATCH /session/clients/user/v1/sessions/{sessionId}
response = requests.patch(
        "https://api.comdirect.de/api/session/clients/user/v1/sessions/%s" % session_id,
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Authorization":"Bearer "+access_token,
            "x-http-request-info":"{\"clientRequestId\":{\"sessionId\":\"%s\",\"requestId\":\"%s\"}}" % (session_id, currenttime()),
            "Content-Type":"application/json",
            "x-once-authentication-info":"{\"id\":\"%s\"}" % challenge_id,
            "x-once-authentication":challenge_tan,
        },
        data='{"identifier":"%s","sessionTanActive":true,"activated2FA":true}' % session_id,
)
print("got response: " + response.text)
tmp = response.json()
session_id = tmp["identifier"] # should not have changed, but anyway

# POST https://api.comdirect.de/oauth/token
response = requests.post(
        "https://api.comdirect.de/oauth/token",
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/x-www-form-urlencoded",
        },
        data = "client_id=%s&client_secret=%s&grant_type=cd_secondary&token=%s" % (client_id, client_secret, access_token),
)
print("got response: " + response.text)
tmp = response.json()
access_token = tmp["access_token"]
refresh_token = tmp["refresh_token"]
kdnr = tmp["kdnr"] # Kundennummer / number of customer
bpid = tmp["bpid"]            # no clue what this is
kontakt_id = tmp["kontaktId"] # no clue what this is 

# GET /banking/clients/user/v1/accounts/balances
response = requests.get(
        "https://api.comdirect.de/api/banking/clients/user/v1/accounts/balances",
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/json",
            "Authorization":"Bearer "+access_token,
            "x-http-request-info":"{\"clientRequestId\":{\"sessionId\":\"%s\",\"requestId\":\"%s\"}}" % (session_id, currenttime()),
         },
        data = "client_id=%s&client_secret=%s&grant_type=cd_secondary&token=%s" % (client_id, client_secret, access_token),
)
print("got response: " + response.text)

# GET /brokerage/clients/user/v3/depots
response = requests.get(
        "https://api.comdirect.de/api/brokerage/clients/user/v3/depots",
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/json",
            "Authorization":"Bearer "+access_token,
            "x-http-request-info":"{\"clientRequestId\":{\"sessionId\":\"%s\",\"requestId\":\"%s\"}}" % (session_id, currenttime()),
        },
        )
print("got response: " + response.text)
tmp = response.json()
depot_id = tmp["values"][0]["depotId"] 

# GET /brokerage/v3/depots/{depotId}/transactions
response = requests.get(
        "https://api.comdirect.de/api/brokerage/v3/depots/%s/transactions?wkn=A1JA1R&max-bookingdate=2017-01-01" % depot_id,
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/json",
            "Authorization":"Bearer "+access_token,
            "x-http-request-info":"{\"clientRequestId\":{\"sessionId\":\"%s\",\"requestId\":\"%s\"}}" % (session_id, currenttime()),
        },
)
print("got response: " + response.text)




# DELETE https://api.comdirect.de/oauth/revoke
response = requests.delete(
        "https://api.comdirect.de/oauth/revoke",
        allow_redirects=False,
        headers = {
            "Accept":"application/json",
            "Authorization":"Bearer "+access_token,
            "Content-Type":"application/x-www-form-urlencoded",
        },
        data='{"identifier":"%s","sessionTanActive":true,"activated2FA":true}' % session_id,
)
print("token revoked")

