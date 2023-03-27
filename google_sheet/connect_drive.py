import os
import gspread
import utils.connect_db as db
from dotenv import load_dotenv
from datetime import date, timedelta

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

load_dotenv()

GOOGLE_DRIVE_ID = os.getenv('GOOGLE_DRIVE_ID', None)
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/spreadsheets"]


def create_credential():
    client_secret = os.path.abspath("client_secret.json")
    # define store
    store = file.Storage("./google_sheet/credentials.json")
    credentials = store.get()
    # get access token
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret, SCOPES)
        credentials = tools.run_flow(flow, store)
        # define API service
        http = credentials.authorize(Http())
        drive = discovery.build('drive', 'v3', http=http)
        return drive


def create_file_in_drive():
    # CHECK CREDENTIAL
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('./google_sheet/credentials.json'):
        creds = Credentials.from_authorized_user_file(
            './google_sheet/credentials.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './google_sheet/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('./google_sheet/credentials.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # create drive api client
            service = discovery.build('drive', 'v3', credentials=creds)
            last_2_day = ((date.today() + timedelta(hours=7)) -
                          timedelta(days=2))
            year = last_2_day.strftime("%Y")
            month = last_2_day.strftime("%B")
            file_name = f'{year}_{month}_KubotaStoreTemplate'
            file_metadata = {
                'name': file_name,
                'parents': [GOOGLE_DRIVE_ID],
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            }
            file = service.files().create(body=file_metadata,
                                          fields='id').execute()
            print(F'File ID: "{file.get("id")}".')
            db.stored_sheet_id(year=year, month=month,
                               sheet_id=file.get('id'), sheet_name=file_name)

            # REVISED SHEET NAMES
            gc = gspread.oauth(
                credentials_filename=os.path.abspath("client_secret.json"),
                authorized_user_filename=os.path.abspath(
                    "./google_sheet/credentials.json")
            )
            sh = gc.open_by_key(file.get('id'))
            try:
                sh.worksheet("Summary")
            except gspread.WorksheetNotFound:
                sh.add_worksheet(title="Summary", rows=100, cols=30)
                sh.add_worksheet(title="MAGENTO", rows=100, cols=30)
                sh.del_worksheet(sh.sheet1)

                # FORMAT WORKSHEET
                sh.worksheet("Summary").format('A2:J2', {
                    "backgroundColor": {
                        "red": 0.5,
                        "green": 0.6,
                        "blue": 0.6
                    },
                    "horizontalAlignment": "CENTER",
                    "wrapStrategy": "LEGACY_WRAP",
                    "textFormat": {
                        "fontSize": 10,
                        "bold": True
                    }
                })
                sh.worksheet("Summary").format('A:J', {
                    "horizontalAlignment": "CENTER"
                })
                sh.worksheet("Summary").format('B:H', {
                    "numberFormat": {
                        "type": "NUMBER",
                        "pattern": "#,###.00"
                    }

                })
                sh.worksheet("Summary").format('J:J', {
                    "numberFormat": {
                        "type": "PERCENT",
                        "pattern": "#.0%"
                    }

                })

                sh.worksheet("MAGENTO").format('A1:X1', {
                    "backgroundColor": {
                        "red": 0.5,
                        "green": 0.6,
                        "blue": 0.6
                    },
                    "horizontalAlignment": "CENTER",
                    "wrapStrategy": "LEGACY_WRAP",
                    "textFormat": {
                        "fontSize": 10,
                        "bold": True
                    }
                })

            return file.get('id')

        except HttpError as error:
            print(F'An error occurred: {error}')
            return None


def update_magento_sheet(sheet_id, sheet_name, data):
    # CHECK CREDENTIAL
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('./google_sheet/credentials.json'):
        creds = Credentials.from_authorized_user_file(
            './google_sheet/credentials.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './google_sheet/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('./google_sheet/credentials.json', 'w') as token:
                token.write(creds.to_json())

    gc = gspread.oauth(
        credentials_filename=os.path.abspath("client_secret.json"),
        authorized_user_filename=os.path.abspath(
            "./google_sheet/credentials.json")
    )

    # year = ((date.today() + timedelta(hours=7))).strftime("%Y")
    # month = ((date.today() + timedelta(hours=7))).strftime("%B")
    # sheet_id = db.get_sheet_of_month(year, month)
    sh = gc.open_by_key(sheet_id)

    worksheet = sh.worksheet(sheet_name)
    print(data[0][2])
    cell = worksheet.find(data[0][2])
    if (cell and cell.row):
        worksheet.update(f'A{cell.row}:AD{cell.row}', data)
    else:
        sh.values_append(
            sheet_name, {"valueInputOption": "USER_ENTERED"}, {"values": data})
    return
