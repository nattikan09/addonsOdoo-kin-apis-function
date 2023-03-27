import calendar
import pandas as pd
import utils.connect_db as db
import payment2c2p.p2c2p_api as pm
import google_sheet.connect_drive as drive
import google_sheet.commission_master as sheet
import odoo.odoo as odoo
from dotenv import load_dotenv
from dateutil.rrule import rrule, DAILY
from datetime import date, datetime, timedelta

load_dotenv()


def calculate_commission(data: dict):
    vat = 1.07
    for item in data:
        commission_acc = 0
        if (item["status"] == "canceled"):
            commission_acc = 0
            item["commission_price"] = commission_acc
        else:
            for i in item["items"]:
                price_per_unit_no_vat = round(i["price"]*(7/107), 2)
                price_no_vat = i["price"] - price_per_unit_no_vat
                price_with_qty = price_no_vat*i["qty_ordered"]
                group = db.find_commission_group(i["sku"])
                if (group != "no group commission"):
                    com_rate = int(sheet.get_commission_rate(group))
                    com_price = round(price_with_qty*(com_rate/100)*vat, 6)
                    commission_acc += com_price
            item["commission_price"] = commission_acc
    return data


def magento_format(data: dict):
    data_frame = pd.DataFrame([])
    for item in data:
        df = pd.json_normalize(item, max_level=1)
        df_shipping = pd.json_normalize(
            item["extension_attributes"], record_path=['shipping_assignments'])
        df["calc_pmt"] = df["payment.method"].values[0] if df["payment.method"].values[0] == "cashondelivery" else pm.get_payment_method(
            df["increment_id"].values[0])
        df["Purchase Date"] = f"{(datetime.strptime(df['created_at'].values[0], '%Y-%m-%d %H:%M:%S')+ timedelta(hours=7)).strftime('%d/%m/%Y %H:%M')}"
        df["Bill-to Name"] = f"{df['billing_address.firstname'].values[0]} {df['billing_address.lastname'].values[0]}"
        df["Ship-to Name"] = f"{df_shipping['shipping.address.firstname'].values[0]} {df_shipping['shipping.address.lastname'].values[0]}"
        df["Billing Address"] = f"{df['billing_address.street'].values[0][0]},{df['billing_address.city'].values[0]},{df['billing_address.region'].values[0]},{df['billing_address.postcode'].values[0]}"
        df["Shipping Address"] = f"{df_shipping['shipping.address.street'].values[0][0]},{df_shipping['shipping.address.city'].values[0]},{df_shipping['shipping.address.region'].values[0]},{df_shipping['shipping.address.postcode'].values[0]}"
        df["Customer Email"] = f"{df_shipping['shipping.address.email'].values[0]}"
        df["Customer Name"] = f"{df['customer_firstname'].values[0]} {df['customer_lastname'].values[0]}"
        data_frame = data_frame.append(df)

    data_with_format = pd.DataFrame(data_frame, columns=[
                                    "commission_price", "calc_pmt", "increment_id", "store_name", "Purchase Date", "Bill-to Name", "Ship-to Name", "base_grand_total", "grand_total", "status", "Billing Address", "Shipping Address", "shipping_description", "Customer Email", "customer_group_id", "subtotal", "base_shipping_amount", "Customer Name", "payment.method", "Total Refunded", "Signifyd Guarantee Decision", "Includes Bundle Pack", "Bundle Pack(s)", "Dealers"])
    data_with_format.rename(columns={"commission_price": "calc_com", "increment_id": "ID", "store_name": "Purchase Point",
                                     "base_grand_total": "Grand Total (Base)", "grand_total": "Grand Total (Purchased)", "status": "Status", "shipping_description": "Shipping Information", "customer_group_id": "Customer Group", "subtotal": "Subtotal", "base_shipping_amount": "Shipping and Handling", "payment.method": "Payment Method"}, inplace=True)
    data_with_format.fillna(0, inplace=True)
    return data_with_format


def report_summary(sheet_id):
    last_2_day = ((date.today() + timedelta(hours=7)) - timedelta(days=2))
    last_date = calendar.monthrange(
        int(last_2_day.strftime("%Y")), int(last_2_day.strftime("%m")))[1]

    # initializing the start and end date
    start_date = date(int(last_2_day.strftime("%Y")),
                      int(last_2_day.strftime("%m")), 1)
    end_date = date(int(last_2_day.strftime("%Y")), int(
        last_2_day.strftime("%m")), int(last_date))

    date_lists = []
    row = 2
    # iterating over the dates
    for d in rrule(DAILY, dtstart=start_date, until=end_date):
        row = row+1
        date_lists.append([d.strftime("%d/%m/%Y"),
                           f'=SUMIFS(MAGENTO!$I:$I,MAGENTO!$E:$E,">="&$A{row},MAGENTO!$E:$E,"<"&$A{row+1},MAGENTO!$J:$J,"<>canceled")',
                           f'=SUMIFS(MAGENTO!$A:$A,MAGENTO!$E:$E,">="&$A{row},MAGENTO!$E:$E,"<"&$A{row+1},MAGENTO!$J:$J,"<>canceled")',
                           f'=B{row}-C{row}',
                           f'=SUMIFS(MAGENTO!$I:$I,MAGENTO!$E:$E,">="&$A{row},MAGENTO!$E:$E,"<"&$A{row+1},MAGENTO!$J:$J,"<>canceled",MAGENTO!$B:$B,E$1)',
                           f'=SUMIFS(MAGENTO!$I:$I,MAGENTO!$E:$E,">="&$A{row},MAGENTO!$E:$E,"<"&$A{row+1},MAGENTO!$J:$J,"<>canceled",MAGENTO!$B:$B,F$1)',
                           f'=SUMIFS(MAGENTO!$I:$I,MAGENTO!$E:$E,">="&$A{row},MAGENTO!$E:$E,"<"&$A{row+1},MAGENTO!$J:$J,"<>canceled",MAGENTO!$B:$B,G$1)',
                           f'=SUM(E{row}:G{row})',
                           f'=B{row}=H{row}',
                           f'=IF(B{row}=0,"",C{row}/B{row})'
                           ])
    header_lists = [["", "", "", "", "cash",
                     "cashondelivery", "ccpp", "", "", ""]]
    df = pd.DataFrame(date_lists, columns=[
                      "Date", "SOCust (New)", "SOSKC", "POSKC", "Cash", "COD", "2C2P", "Total", "CHECK", "Rate"])
    data_lists = (
        header_lists+[df.columns.values.tolist()] + df.values.tolist())
    drive.update_magento_sheet(sheet_id, "Summary", data_lists)
    print(data_lists)
    return df.values.tolist()


def export_to_magento(data_with_format):
    last_2_day = ((date.today() + timedelta(hours=7)) - timedelta(days=2))
    year = last_2_day.strftime("%Y")
    month = last_2_day.strftime("%B")
    sheet_id = db.get_sheet_of_month(year, month)

    if not sheet_id:
        sheet_id = drive.create_file_in_drive()
        report_summary(sheet_id)
        data_lists = ([data_with_format.columns.values.tolist()] +
                      data_with_format.values.tolist())
        return drive.update_magento_sheet(sheet_id, "MAGENTO", data_lists)
    else:
        return drive.update_magento_sheet(sheet_id, "MAGENTO", data_with_format.values.tolist())


def update_to_magento(data_with_format):
    return drive.update_magento_sheet("MAGENTO", data_with_format)
