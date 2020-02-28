import requests
import uuid
import datetime
import base64
import io
import json
import time


def currenttime():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")


def is_valid_TAN(tan):
    return type(tan) == str and len(tan) == 6 and set(tan) <= set("0123456789")


def default_callback_photo_tan(pngImage):
    from PIL import Image

    Image.open(io.BytesIO(pngImage)).show()
    photo_tan = input("Please enter Photo-TAN: ")
    if not is_valid_TAN(photo_tan):
        raise ValueError(f"invalid Photo-TAN {photo_tan}")
    return photo_tan


def default_callback_sms_tan():
    sms_tan = input("Please enter your SMS-TAN: ")
    if not is_valid_TAN(sms_tan):
        raise ValueError(f"invalid SMS-TAN {sms_tan}")
    return sms_tan


class Session:
    def __init__(
        self,
        username,
        password,
        client_id,
        client_secret,
        callback_photo_tan=default_callback_photo_tan,
        callback_sms_tan=default_callback_sms_tan,
        autorefresh=False,
    ):
        self.autorefresh = autorefresh

        # POST /oauth/token
        response = requests.post(
            "https://api.comdirect.de/oauth/token",
            f"client_id={client_id}&"
            f"client_secret={client_secret}"
            f"&username={username}&"
            f"password={password}&"
            f"grant_type=password",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if not response.status_code == 200:
            raise RuntimeError(
                f"POST https://api.comdirect.de/oauth/token returned status {response.status_code}"
            )
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
                "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{self.session_id}",'
                f'requestId":"{currenttime()}"}}}}',
            },
        )
        if not response.status_code == 200:
            raise RuntimeError(
                f"GET https://api.comdirect.de/api/session/clients/user/v1/sessions returned status {response.status_code}"
            )
        tmp = response.json()
        self.session_id = tmp[0]["identifier"]

        # POST /session/clients/user/v1/sessions/{sessionId}/validate
        response = requests.post(
            f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{self.session_id}/validate",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{self.session_id}","requestId":"{currenttime()}"}}}}',
                "Content-Type": "application/json",
            },
            data=f'{{"identifier":"{self.session_id}","sessionTanActive":true,"activated2FA":true}}',
        )
        if response.status_code != 201:
            raise RuntimeError(
                f"POST /session/clients/user/v1/sessions/.../validate returned status code {response.status_code}"
            )
        tmp = json.loads(response.headers["x-once-authentication-info"])
        challenge_id = tmp["id"]
        challenge = tmp["challenge"]
        typ = tmp["typ"]
        if typ == "P_TAN":
            if callback_photo_tan:
                tan = callback_photo_tan(base64.b64decode(challenge))
            else:
                # TODO: we could retry with other TAN type...
                raise RuntimeError(
                    "cannot handle photo tan because you did not provide handler"
                )
        elif typ == "M_TAN":
            if callback_sms_tan:
                tan = callback_sms_tan()
            else:
                # TODO: we could retry with other TAN type...
                raise RuntimeError(
                    "cannot handle SMS tan because you did not provide handler"
                )
        else:
            raise RuntimeError(f"unknown TAN type {typ} with challenge {challenge}")

        # PATCH /session/clients/user/v1/sessions/{sessionId}
        response = requests.patch(
            f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{self.session_id}",
            allow_redirects=False,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
                "x-http-request-info": f'{{"clientRequestId":{{"sessionId":"{self.session_id}","requestId":"{currenttime()}"}}}}',
                "Content-Type": "application/json",
                "x-once-authentication-info": f'{{"id":"{challenge_id}"}}',
                "x-once-authentication": tan,
            },
            data=f'{{"identifier":"{self.session_id}","sessionTanActive":true,"activated2FA":true}}',
        )
        tmp = response.json()
        if not response.status_code == 200:
            raise RuntimeError(
                f"PATCH https://api.comdirect.de/session/clients/user/v1/sessions/... returned status {response.status_code}"
            )
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
        print("access response: " + response.text)
        if not response.status_code == 200:
            raise RuntimeError(
                f"POST https://api.comdirect.de/oauth/token returned status {response.status_code}"
            )
        tmp = response.json()
        self.access_token = tmp["access_token"]
        self.refresh_token = tmp["refresh_token"]
        self.kdnr = tmp["kdnr"]  # Kundennummer / number of customer
        self.bpid = tmp["bpid"]  # no clue what this is
        self.kontakt_id = tmp["kontaktId"]  # no clue what this is
        self.isRevoked = False

        if self.autorefresh:
            self.refreshThread = threading.Thread(target=self._refresh_worker)
            self.refreshThread.start()

    def _refresh_worker(self):
        while not self.isRevoked:
            time.sleep(9 * 60)
            if self.isRevoked:
                break
            else:
                self.refresh()

    def revoke(self):
        if not self.isRevoked:
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
            print(response.text)
            print(response.status_code)
            if not response.status_code == 204:
                raise RuntimeError(
                    f"DELETE https://api.comdirect.de/oauth/revoke returned unexpected status {response.status_code}"
                )
            self.isRevoked = True

    def refresh(self):
        # https://api.comdirect.de/oauth/revoke
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
        print(response.text)
        print(response.status_code)
        if not response.status_code == 204:
            raise RuntimeError(
                f"DELETE https://api.comdirect.de/oauth/revoke returned unexpected status {response.status_code}"
            )
        self.isRevoked = True
