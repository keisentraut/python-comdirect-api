import requests
import uuid
import datetime
import base64
import io
import json
from PIL import Image


def currenttime():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")

def is_valid_TAN(tan):
    return type(tan) == str and len(tan) == 6 and set(tan) <= set("0123456789")

def default_callback_photo_tan(pngImage):
    Image.open(io.BytesIO(pngImage)).show()
    photo_tan = input("Please enter Photo-TAN: ")
    if not is_valid_TAN(photo_tan):
        raise ValueError(f"invalid Photo-TAN {challenge_tan}")
    return photo_tan 

def default_callback_sms_tan():
    sms_tan = input("Please enter your SMS-TAN: ")
    if not is_valid_TAN(sms_tan):
        raise ValueError(f"invalid SMS-TAN {challenge_tan}")
    return sms_tan


class Session():
    def __init__(self, client_id, client_secret, username, password, 
            callback_photo_tan=default_callback_photo_tan,
            callback_sms_tan=None,
            autorenew=True):
        # POST /oauth/token
        response = requests.post(
            "https://api.comdirect.de/oauth/token",
            f"client_id={client_id}&client_secret={client_secret}&username={username}&password={password}&grant_type=password",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if not response.status_code == 200:
            raise ValueError(f"POST https://api.comdirect.de/oauth/token returned status {response.status_code}")
        tmp = response.json()
        self.access_token = tmp["access_token"]
        self.refresh_token = tmp["refresh_token"]

        # GET /session/clients/user/v1/sessions
        self.session_id = uuid.uuid4()
        response = requests.get(
            "https://api.comdirect.de/api/session/clients/user/v1/sessions",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{session_id}","requestId":"{currenttime()}"}}}}',
            },
        )
        if not response.status_code == 200:
            raise ValueError(f"GET https://api.comdirect.de/api/session/clients/user/v1/sessions returned status {response.status_code}")
        tmp = response.json()
        self.session_id = tmp[0]["identifier"]

        # POST /session/clients/user/v1/sessions/{sessionId}/validate
        response = requests.post(
            f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{session_id}/validate",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer " + access_token,
                "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{session_id}","requestId":"{currenttime()}"}}}}',
                "Content-Type": "application/json",
            },
            data='{"identifier":"%s","sessionTanActive":true,"activated2FA":true}'
            % session_id,
        )

        tmp = json.loads(response.headers["x-once-authentication-info"])
        challenge_id = tmp["id"]
        challenge = tmp["challenge"]


    def __del__(self):
        # DELETE https://api.comdirect.de/oauth/revoke
        response = requests.delete(
            "https://api.comdirect.de/oauth/revoke",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f'{{"identifier":"{self.session_id}","sessionTanActive":true,"activated2FA":true}}',
        )
        if not response.status_code == 204:
            raise ValueError(f"DELETE https://api.comdirect.de/oauth/revoke returned unexpected status {response.status_code}")
        print("token revoked")


    def _autorenew(self):
        # TODO: implement me
        

def authorization(client_id, client_secret, username, password):

    # PATCH /session/clients/user/v1/sessions/{sessionId}
    response = requests.patch(
        "https://api.comdirect.de/api/session/clients/user/v1/sessions/%s" % session_id,
        allow_redirects=False,
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer " + access_token,
            "x-http-request-info": '{"clientRequestId":{"sessionId":"%s","requestId":"%s"}}'
            % (session_id, currenttime()),
            "Content-Type": "application/json",
            "x-once-authentication-info": '{"id":"%s"}' % challenge_id,
            "x-once-authentication": challenge_tan,
        },
        data='{"identifier":"%s","sessionTanActive":true,"activated2FA":true}'
        % session_id,
    )

    tmp = response.json()
    session_id = tmp["identifier"]

    # POST https://api.comdirect.de/oauth/token
    response = requests.post(
        "https://api.comdirect.de/oauth/token",
        allow_redirects=False,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="client_id=%s&client_secret=%s&grant_type=cd_secondary&token=%s"
        % (client_id, client_secret, access_token),
    )
    # print("access response: " + response.text)
    tmp = response.json()
    access_token = tmp["access_token"]
    refresh_token = tmp["refresh_token"]
    kdnr = tmp["kdnr"]  # Kundennummer / number of customer
    bpid = tmp["bpid"]  # no clue what this is
    kontakt_id = tmp["kontaktId"]  # no clue what this is
    accountId = "8F87391AA00D44FBB7C780069A7020E5"
    return accountId, access_token, session_id


def revoke_token(access_token, session_id):
    
def get_requests(url, access_token, session_id, client_id, client_secret, filename):
    response = requests.get(
        url,
        allow_redirects=False,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + access_token,
            "x-http-request-info": '{"clientRequestId":{"sessionId":"%s","requestId":"%s"}}'
            % (session_id, currenttime()),
        },
        data="client_id=%s&client_secret=%s&grant_type=cd_secondary&token=%s"
        % (client_id, client_secret, access_token),
    )
    with open(filename, "w") as outfile:
        outfile.write(response.text)
    if url == "https://api.comdirect.de/api/brokerage/clients/user/v3/depots":
        tmp = response.json()
        return tmp["values"][0]["depotId"]
    else:
        return None


def main_requests(
    client_id,
    client_secret,
    username,
    password,
    min_transactiondate,
    max_transactiondate,
    currentdir,
):
    accountId, access_token, session_id = authorization(
        client_id, client_secret, username, password
    )
    url = (
        "https://api.comdirect.de/api/banking/v1/accounts/%s/transactions"
        "?min-bookingdate[gte]=%s&max-bookingdate[lte]=%s"
        % (accountId, min_transactiondate, max_transactiondate)
    )
    filename = currentdir + "/balance_transactions.json"
    response = get_requests(
        url, access_token, session_id, client_id, client_secret, filename
    )
    url = "https://api.comdirect.de/api/brokerage/clients/user/v3/depots"
    filename = currentdir + "/depot_information.json"
    depot_id = get_requests(
        url, access_token, session_id, client_id, client_secret, filename
    )
    url = (
        "https://api.comdirect.de/api/brokerage/v3/depots/%s/transactions"
        "?min-bookingdate[gte]=%s&max-bookingdate[lte]=%s"
        % (depot_id, min_transactiondate, max_transactiondate)
    )
    filename = currentdir + "/depot_transactions.json"
    response = get_requests(
        url, access_token, session_id, client_id, client_secret, filename
    )
    url = "https://api.comdirect.de/api/brokerage/v3/depots/%s/positions" % depot_id
    filename = currentdir + "/depot_positions.json"
    response = get_requests(
        url, access_token, session_id, client_id, client_secret, filename
    )
    revoke_token(access_token, session_id)


if __name__ == "__main__":
    main_requests()
