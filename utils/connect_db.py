import os
from dotenv import load_dotenv
from datetime import date, timedelta
from azure.data.tables import TableServiceClient, UpdateMode
from azure.storage.blob import BlobServiceClient, BlobClient, ResourceTypes, AccountSasPermissions, generate_account_sas, StandardBlobTier

load_dotenv()

STORAGE_ACC_NAME = os.getenv('STORAGE_ACC_NAME', None)
STORAGE_KEY = os.getenv('STORAGE_KEY', None)
STORAGE_TABLE = os.getenv('STORAGE_TABLE', None)
MASTER_COMMISSION_ITEM = os.getenv('MASTER_COMMISSION_ITEM', None)
MASTER_GOOGLE_SHEET = os.getenv('MASTER_GOOGLE_SHEET', None)

CONNECTIONSTRING = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACC_NAME};AccountKey={STORAGE_KEY};EndpointSuffix=core.windows.net"

table_service = TableServiceClient.from_connection_string(CONNECTIONSTRING)
table_client = table_service.get_table_client(STORAGE_TABLE)
master_com_table = table_service.get_table_client(MASTER_COMMISSION_ITEM)
master_sheet_table = table_service.get_table_client(MASTER_GOOGLE_SHEET)


def get_data_by_service(service: str):
    query_filter = f"PartitionKey eq '{service}'"
    queried_entities = table_client.query_entities(query_filter)
    lenght = len(list(queried_entities))
    if (lenght > 0):
        for item in queried_entities.by_page():
            return [i for i in item]
    return []


def stored_magento_data(data: dict):
    last_2_day = ((date.today() + timedelta(hours=7)) -
                  timedelta(days=2)).strftime('%Y_%m')
    for item in data:
        table_client.create_entity({
            "PartitionKey": "magento",
            "RowKey": item.get("increment_id"),
            "year_month": last_2_day,
            "status": item.get("status"),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
        })
    return get_data_by_service("magento")


def get_re_order_data():
    last_2_day = ((date.today() + timedelta(hours=7)) -
                  timedelta(days=5)).strftime('%Y_%m')
    query_filter = f"PartitionKey eq 'magento' and year_month eq '{last_2_day}'"
    queried_entities = table_client.query_entities(query_filter)
    lenght = len(list(queried_entities))
    if (lenght > 0):
        for item in queried_entities.by_page():
            return [i["RowKey"] for i in item]
    return []


def delete_re_order_data(rowKey: str):
    return table_client.delete_entity('magento', rowKey)


def update_commission_master(data: dict):
    for item in data:
        master_com_table.upsert_entity({
            "PartitionKey": "com_master",
            "RowKey": item[1],
            "material_no": item[1],
            "material_name_en": item[2],
            "material_name_th": item[3],
            "group": item[4],
            "slp_vat": item[5],
            "effecive_date": item[6],
            "division": item[7],
            "product": item[8],
        })
    return {"status": "finished"}


def find_commission_group(item: str):
    query_filter = f"RowKey eq '{item}'"
    queried_entities = master_com_table.query_entities(query_filter)
    lenght = len(list(queried_entities))
    if (lenght > 0):
        for item in queried_entities.by_page():
            for i in item:
                group = i["group"]
    else:
        group = "no group commission"
    return group


def get_sheet_of_month(year: str, month: str):
    query_filter = f"year eq '{year}' and month eq '{month}'"
    queried_entities = master_sheet_table.query_entities(query_filter)
    lenght = len(list(queried_entities))
    if (lenght > 0):
        for item in queried_entities.by_page():
            return [i["sheet_id"] for i in item][0]
    return []


def stored_sheet_id(year: str, month: str, sheet_id: str, sheet_name: str):
    query_filter = f"sheet_id eq '{sheet_id}'"
    queried_entities = master_sheet_table.query_entities(query_filter)
    lenght = len(list(queried_entities))
    if not (lenght > 0):
        master_sheet_table.create_entity({
            "PartitionKey": "magento",
            "RowKey": sheet_name,
            "year": year,
            "month": month,
            "sheet_id": sheet_id
        })
    return get_sheet_of_month(year, month)
