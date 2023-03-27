import gspread
import json
import pygsheets
import requests
# import pandas as pd
# import df2gspread as d2g
import utils.connect_db as db
import google_sheet.connect_google as gg
from dotenv import load_dotenv
from datetime import date, timedelta
from google.oauth2.credentials import Credentials

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/spreadsheets"]


def update_magento_sheet(magento_data: json):
    r = gg.refresh_access_token()
    data = r.json()

    year = ((date.today() + timedelta(hours=7))).strftime("%Y")
    month = ((date.today() + timedelta(hours=7))).strftime("%B")
    sheet_id = db.get_sheet_of_month(year, month)
    print(sheet_id)

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}:batchUpdate"
    headers = {
        "Authorization": f"{data.get('token_type')} {data.get('access_token')}"
    }
    body = {
        "requests": [],
        "includeSpreadsheetInResponse": False,
        "responseRanges": [],
        "responseIncludeGridData": False
    }
    r = requests("POST", url, data=(magento_data), headers=headers)
    return
