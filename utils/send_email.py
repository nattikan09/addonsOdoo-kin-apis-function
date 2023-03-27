import os
import smtplib
import utils.connect_db as db
from tabulate import tabulate
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

HOST = os.getenv('EMAIL_HOST', None)
PORT = os.getenv('EMAIL_PORT', None)
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', None)


def send_email_notify():
    orders = db.get_re_order_data()
    print(type(orders))
    if (orders and len(orders) > 0):
        sender = 'waraporn.v@kasetinno.com'
        receivers = ['waraporn.v@kubota.com']
        subject = "แจ้งเตือน Magento Orders ที่ยังทำรายการไม่สำเร็จ"

        text = """
เรียนทุกท่าน

ข้อมูล Orders ที่ยังทำรายการไม่สำเร็จ รายละเอียดตามตารางด้านล่าง:
{table}

Regards,
Me"""
#         html = """
# <html><body><p>Hello, Friend.</p>
# <p>Here is your data:</p>
# {table}
# <p>Regards,</p>
# <p>Me</p>
# </body></html>
# """
        # text = text.format(table=tabulate(
        #     orders, headers="firstrow", tablefmt="grid"))
        print(text)
        # html = html.format(table=tabulate(
        #     orders, headers="firstrow", tablefmt="html"))
        # message = MIMEMultipart(
        #     "alternative", None, [MIMEText(text, 'plain'), MIMEText(html,'html')])
        message = MIMEMultipart(
            "alternative", None, [MIMEText(text, 'plain')])

        message['Subject'] = subject
        message['From'] = sender
        message['To'] = receivers
        print(text)

        try:
            print("Before sent")
            smtpObj = smtplib.SMTP(HOST)
            smtpObj.starttls()
            smtpObj.login('waraporn.v@kasetinno.com', EMAIL_PASSWORD)
            smtpObj.sendmail(sender, receivers, message)
            print("Successfully sent email")
        except smtplib.SMTPException as e:
            print(e)
            return
