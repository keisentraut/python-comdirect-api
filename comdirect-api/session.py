import requests
import uuid
import datetime
import base64
import io
import json

def currenttime():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")

def is_valid_TAN(tan):
    return type(tan) == str and len(tan) == 6 and set(tan) <= set("0123456789")

def default_callback_photo_tan(pngImage):
    from PIL import Image
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
            callback_photo_tan = default_callback_photo_tan,
            callback_sms_tan   = default_callback_sms_tan,
            autorenew=True):
        self.autorenew = autorenew 

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
                "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{self.session_id}","requestId":"{currenttime()}"}}}}',
            },
        )
        if not response.status_code == 200:
            raise ValueError(f"GET https://api.comdirect.de/api/session/clients/user/v1/sessions returned status {response.status_code}")
        tmp = response.json()
        self.session_id = tmp[0]["identifier"]

        # POST /session/clients/user/v1/sessions/{sessionId}/validate
        response = requests.post(
            f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{self.session_id}/validate",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer {self.access_token}",
                "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{self.session_id}","requestId":"{currenttime()}"}}}}',
                "Content-Type": "application/json",
            },
            data=f'{{"identifier":"{self.session_id}","sessionTanActive":true,"activated2FA":true}}',
        )
        if response.status_code != 201:
            raise RuntimeError(f"POST /session/clients/user/v1/sessions/.../validate returned status code {response.status_code}")
        tmp = json.loads(response.headers["x-once-authentication-info"])
        challenge_id = tmp["id"]
        challenge = tmp["challenge"]
        typ = tmp["typ"]
        if typ == "P_TAN":
            if callback_photo_tan:
                tan = callback_photo_tan(base64.b64decode(challenge))
            else:
                # TODO: we could retry with other TAN type...
                raise RuntimeError("cannot handle photo tan because you did not provide handler")
        elif typ == "M_TAN":
            if callback_sms_tan:
                tan = callback_sms_tan()
            else:
                # TODO: we could retry with other TAN type...
                raise RuntimeError("cannot handle SMS tan because you did not provide handler")
        else:
            raise RuntimeError(f"unknown TAN type {typ} with challenge {challenge}")

        # PATCH /session/clients/user/v1/sessions/{sessionId}
        response = requests.patch(
            f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{self.session_id}",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "x-http-request-info": f'{{clientRequestId":{{sessionId":"{self.session_id}","requestId":"{currenttime()}"}}}}',
                "Content-Type": "application/json",
                "x-once-authentication-info": f'{{"id":"{challenge_id}"}}',
                "x-once-authentication": challenge_tan,
            },
            data=f'{{"identifier":"{self.session_id}","sessionTanActive":true,"activated2FA":true}}',
        )
        tmp = response.json()
        self.session_id = tmp["identifier"]
        # POST https://api.comdirect.de/oauth/token
        response = requests.post(
            "https://api.comdirect.de/oauth/token",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f"client_id={client_id}&client_secret={client_secret}&grant_type=cd_secondary&token={self.access_token}",
        )
        # print("access response: " + response.text)
        tmp = response.json()
        self.access_token = tmp["access_token"]
        self.refresh_token = tmp["refresh_token"]
        self.kdnr = tmp["kdnr"]  # Kundennummer / number of customer
        self.bpid = tmp["bpid"]  # no clue what this is
        self.kontakt_id = tmp["kontaktId"]  # no clue what this is

    def __del__(self):
        # DELETE https://api.comdirect.de/oauth/revoke
        response = requests.delete(
            "https://api.comdirect.de/oauth/revoke",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=f'{{"identifier":"{self.session_id}","sessionTanActive":true,"activated2FA":true}}',
        )
        if not response.status_code == 204:
            raise ValueError(f"DELETE https://api.comdirect.de/oauth/revoke returned unexpected status {response.status_code}")
        print("token revoked")


    def renew_token(self):
        print("TODO: renew token is not implemented")
        # TODO: implement me
