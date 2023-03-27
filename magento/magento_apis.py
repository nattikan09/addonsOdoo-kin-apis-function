import os
import requests
import utils.connect_db as db
import magento.export_data as df
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()

MAGENTO_TOKEN = os.getenv('MAGENTO_TOKEN', None)
MAGENTO_URL = os.getenv('MAGENTO_URL', None)


def get_orders():
    # last_2_day = ((date.today() + timedelta(hours=7)) -
    #               timedelta(days=2)).strftime("%Y-%m-%d")
    last_2_day = "2023-03-24"             
    res = requests.get(f"{MAGENTO_URL}/rest/V1/orders",
                       headers={
                           "Authorization": f"Bearer {MAGENTO_TOKEN}"
                       },
                       params={
                           "searchCriteria[filter_groups][0][filters][0][field]": "created_at",
                           "searchCriteria[filter_groups][0][filters][0][value]": f"{last_2_day}%",
                           #    "searchCriteria[filter_groups][0][filters][0][field]": "increment_id",
                           #    "searchCriteria[filter_groups][0][filters][0][value]": "KSO000003624",
                           "searchCriteria[filter_groups][0][filters][0][condition_type]": "like",
                           "fields":
                           "items[items[price,qty_ordered,sku,method],payment[method],increment_id,store_name,created_at,billing_address[firstname,lastname,street,city,region,postcode],extension_attributes[shipping_assignments[shipping[address]]],base_grand_total,grand_total,status,shipping_description,customer_group_id,subtotal,base_shipping_amount,customer_firstname,customer_lastname]",
                       })
    orders = res.json().get("items")
    print(orders)
    if(orders and len(orders) > 0):
        data_with_comm = df.calculate_commission(orders)
        final_data = df.magento_format(data_with_comm)
        print(final_data)
        df.export_to_magento(final_data)
        filter_in_progress(orders)
        return data_with_comm


def get_order_by_id(order_id: str):
    res = requests.get(f"{MAGENTO_URL}/rest/V1/orders?",
                       headers={
                           "Authorization": f"Bearer {MAGENTO_TOKEN}"
                       },
                       params={
                           "searchCriteria[filter_groups][0][filters][0][field]": "increment_id",
                           "searchCriteria[filter_groups][0][filters][0][value]": f"{order_id}",
                           "searchCriteria[filter_groups][0][filters][0][condition_type]": "eq",
                           "fields":
                           "items[items[price,qty_ordered,sku,method],payment[method],increment_id,store_name,created_at,billing_address[firstname,lastname,street,city,region,postcode],extension_attributes[shipping_assignments[shipping[address]]],base_grand_total,grand_total,status,shipping_description,customer_group_id,subtotal,base_shipping_amount,customer_firstname,customer_lastname]",
                       })
    return res.json().get("items")


def filter_in_progress(orders: dict):
    in_progress_orders = list(
        filter(lambda item: ((item.get("status") == "in_progress") | (item.get("status") == "pending") | (item.get("status") == "other")), orders))
    db.stored_magento_data(in_progress_orders)
    return in_progress_orders


def re_order():
    orders = db.get_re_order_data()
    for item in orders:
        data = get_order_by_id(item)
        data_with_comm = df.calculate_commission(data)
        final_data = df.magento_format(data_with_comm)
        df.update_to_magento(final_data)
        db.delete_re_order_data(item)

    ship_data = list(
        filter(lambda item: item.get("status") == "shipped", orders))
    if (len(ship_data) > 0):
        data_with_comm = df.calculate_commission(ship_data)
        df.magento_format(data_with_comm)

    return
