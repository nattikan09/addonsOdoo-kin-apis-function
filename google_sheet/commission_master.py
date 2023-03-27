import os
import requests
import utils.connect_db as db
import google_sheet.connect_google as gg
from dotenv import load_dotenv

load_dotenv()

COM_SHEET_ID = os.getenv('COM_SHEET_ID', None)
SHEET_NAME_COM_MASTER = 'COM_MASTER'
SHEET_NAME_COM_RATE = 'COM_RATE'
COM_SHEET_RANGE = f"{SHEET_NAME_COM_MASTER}!A:I"
COM_RATE_SHEET_RANGE = f"{SHEET_NAME_COM_RATE}!A1:B6"


def update_commission_master():
    r = gg.refresh_access_token()
    data = r.json()

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{COM_SHEET_ID}/values/{COM_SHEET_RANGE}"
    headers = {
        "Authorization": f"{data.get('token_type')} {data.get('access_token')}"
    }

    res = requests.get(url, headers=headers)
    return db.update_commission_master(res.json().get("values"))


def get_commission_rate(group: str):
    r = gg.refresh_access_token()
    data = r.json()

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{COM_SHEET_ID}/values/{COM_RATE_SHEET_RANGE}"
    headers = {
        "Authorization": f"{data.get('token_type')} {data.get('access_token')}"
    }

    res = requests.get(url, headers=headers)
    for item in res.json().get("values"):
        if (item[0] == group):
            com_rate = item[1]
    return com_rate
