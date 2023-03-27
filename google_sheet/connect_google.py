import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID', None)
CLIENT_SECRET = os.getenv('CLIENT_SECRET', None)
REFRESH_TOKEN = "1//0gweWAMR1PZt5CgYIARAAGBASNwF-L9Ir2eUA7IXU5o9seuMOtuyfxSRtyOugbp5SlJz4caoPPwiTMCWEzEb5lLijmf-Jy4mEso0"
ACCESS_CODE = "4/0AWtgzh7pkX8OJmZTFRMK3gS3Tch4XVdjV9v8AdspSBdbmMzTvDJJd_8emTfjNBDg0Cp08g"


def get_refresh_token():
    # get refresh token/access token from access code
    url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "code": ACCESS_CODE,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://www.googleapis.com/auth/spreadsheets",
        "redirect_uri": "http://localhost:8000"
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }

    r = requests.post(url, data=data, headers=headers)
    print(r.text)


def refresh_access_token():
    url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    res = requests.post(url, data=data, headers=headers)
    return res
