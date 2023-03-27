
import utils.connect_db as db
import magento.magento_apis as magento
# import utils.send_email as mail
import google_sheet.commission_master as master
import odoo.odoo as odoo
from dotenv import load_dotenv
from fastapi import APIRouter, Request

load_dotenv()

router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    responses={401: {"message": "You not have permission."}}
)
@router.get("/test")
def read_root():
    return {"Hello": "World"}

@router.get("/magento")
def get_magento_orders(request: Request):
    in_progress_orders = magento.get_orders()
    return in_progress_orders

@router.get("/update/com_master")
def update_master(request: Request):
    return master.update_commission_master()

@router.post("/odoo")    
def send_data(request: Request):
    # Test data create customer invoice and vendor
    # invoice_date = '2023-03-17'
    # price_so_kin_cust = 1000.00
    # price_so_kin_skc = 200.00
    # price_po_kin_skc = 800.00
    result = odoo.send_data(invoice_date, price_so_kin_cust, price_so_kin_skc, price_po_kin_skc) #doc_transaction
    # result = odoo.send_data(x)
    return result


@router.get("/mail")
def send_email(request: Request):
    return mail.send_email_notify()