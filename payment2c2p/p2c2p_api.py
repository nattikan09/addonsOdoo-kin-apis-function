import os
import jwt
import requests
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('2C2P_URL', None)
MERCHANT_ID = os.getenv('MERCHANT_ID', None)
MERCHANT_KEY = os.getenv('MERCHANT_KEY', None)


def encoded_key(payload: dict):
    return jwt.encode(payload, MERCHANT_KEY, algorithm="HS256")


def get_payment_method(invoice_no: str):
    jwt_payload = encoded_key({
        "merchantID": MERCHANT_ID,
        "invoiceNo": invoice_no,
        "locale": "th"
    })
    headers = {
        "accept": "application/json",
        "content-type": "application/*+json"
    }
    res = requests.post(f"{URL}/payment/4.1/paymentInquiry",
                        json={"payload": jwt_payload}, headers=headers)

    response_data = jwt.decode(res.json().get("payload"), MERCHANT_KEY, algorithms="HS256")
    return "ccpp" if response_data.get("paymentScheme") is not None else "cash"
