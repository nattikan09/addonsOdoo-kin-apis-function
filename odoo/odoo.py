
import os
import requests
import xmlrpc.client
import json
from dotenv import load_dotenv
from datetime import date, timedelta, datetime
from collections import OrderedDict
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

load_dotenv()

url = os.getenv('url',None)
db = os.getenv('db', None)
username = os.getenv('OdooUsername', None)
password = os.getenv('OdooPassword', None)

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
version = common.version()
uid = common.authenticate(db, username, password, {})
# Check that the authentication was successful
if not uid:
    print("Failed to authenticate!")
else:
    print("Authenticated successfully with UID: {}".format(uid))

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# odoo=[]

def send_data(invoice_date: str, price_so_kin_cust: float, price_so_kin_skc: float,price_po_kin_skc: float): #doc_transaction: str
    result = create_kstore(invoice_date, price_so_kin_cust, price_so_kin_skc, price_po_kin_skc) #doc_transaction
    return {"result": result}

def create_kstore(invoice_date: str, price_so_kin_cust: float, price_so_kin_skc: float,price_po_kin_skc: float):

    v_invoice_date = invoice_date # order date magento
    v_price_so_kin_cust = price_so_kin_cust 
    v_price_so_kin_skc = price_so_kin_skc
    v_price_po_kin_skc = v_price_so_kin_cust - v_price_so_kin_skc
                
    ##note link## doc_transaction = doc_transaction
    gooelurl = "https://docs.google.com/spreadsheets/d/1fxHltnGfp22djdPEJTSXfJtMDLTCnJfTgX-NkMSWssQ/edit#gid=1623472983"
    doc_transaction =  "<p><a href=\""+gooelurl+";2023_March_KubotaStoreTemplatex&lt;/a&gt;\" target=\"_blank\">"+"Transaction detial"+" "+v_invoice_date+"</a></p>"

    l_invcust_label = 'KUBOTA Store Transaction on ' + v_invoice_date
    l_invskc_label = 'KUBOTA Store Commission on ' + v_invoice_date
    l_vbskc_label = 'KUBOTA Store Less Commission on ' + v_invoice_date

    v_doc_ref = 'KSTOR' + v_invoice_date[0:4] + v_invoice_date[5:7] + v_invoice_date[8:10]
    v_invoice_origin = 'KSTOR' + v_invoice_date[0:4] + v_invoice_date[5:7] + v_invoice_date[8:10]

    v_partner_id = 165
        # v_partner_shipping_id = 165
    v_partner_x_address_cust = 'KUBOTA Store Customers'
    v_partner_x_address_skc = 'บริษัทสยามคูโบต้าคอร์ปอเรชั่น จำกัด (สำนักงานใหญ่)'
    v_move_type = "out_invoice"
        # v_invoice_payment_term_id = 1
        # line
    l_product_kin_cust = 71  # KUBOTA Store Suspense
    l_product_kin_skc = 72  # KUBOTA Store Commission

    v_partner_id_cust = 165  # KUBOTA Store Customer
    v_partner_id_skc = 45  # SKC HQ
    l_product_uom_id = 1
        # l_line_name = 'KUBOTA Store Transaction on '+ v_invoice_date

    v_payment_term_id_immediate = 1  # Immediate
    v_payment_term_id_standard = 10  # Standard

    v_team_id = False

    l_analytic_account_id = 48  # KUBOTA Store (Only for commission)
    l_analytic_account_id_none = False

    v_susp_journal_id = 93  # Suspense
    v_inv_journal_id = 67  # Customer Invoice
    v_vb_journal_id = 70  # Vendor Bill

    v_inv_move_type = 'out_invoice'  # Invoice
    v_vb_move_type = 'in_invoice'  # Vendor Bill

    l_quantity = 1

    tax_none = False
    l_tax_7incl = 107

    l_inv_skc_account_id = 1738
    l_susp_account_id = 1944

    
    # Search for customer invoices matching the specified criteria
    search_criteria = [[['ref','=',v_doc_ref],['move_type','in',('out_invoice','in_invoice')]]]
    fields = {'fields': ['id','move_type','ref']}
    v_doc_ref_check = models.execute_kw(db, uid, password, 'account.move', 'search_read', search_criteria, fields)

    json_data=[]
    result={}
    # Check if any records were found
    if len(v_doc_ref_check) > 0:
        # Print a message indicating that records were found
        check_ref = "Found {} records matching the search criteria:".format(len(v_doc_ref_check),json_data)

        # result = {'Result': check_ref}
        {result:= check_ref}
    else:
        # Print a message indicating that no records were found
        # print("No records found matching the search criteria.")

        ### KUBOTA Store Customer ###
        inv_kubota_store_customer = models.execute_kw(db, uid,password, 'account.move' , 'create' ,[{
                        'date' : v_invoice_date,
                        'partner_id': v_partner_id_cust,
                        'partner_shipping_id':v_partner_id_cust,
                        # 'x_address':v_partner_x_address_cust,
                        'team_id': v_team_id,
                        'invoice_date':v_invoice_date,
                        'invoice_payment_term_id' : v_payment_term_id_immediate,
                        'journal_id': v_susp_journal_id,
                        'move_type': v_inv_move_type,
                        'invoice_origin': v_invoice_origin,
                        'ref': v_doc_ref,
                        'invoice_line_ids':[(0,0,{
                                            'product_id':l_product_kin_cust,
                                            'name':l_invcust_label,
                                            'account_id': l_susp_account_id,
                                            'analytic_account_id': l_analytic_account_id_none,
                                            'quantity':l_quantity,
                                            'price_unit':price_so_kin_cust,
                                            # 'product_uom_id':l_product_uom_id
                                            })]
                            }])
        # link document excel                   
        models.execute_kw(db, uid, password, 'account.move', 'write', [inv_kubota_store_customer, {'narration': doc_transaction}])  
        print("KUBOTA Store Customer = ",inv_kubota_store_customer)

            #post KUBOTA Store Customer
            # posted_invoices = models.execute_kw(db, uid, password,'account.move','action_post',[invoice_ids])

            ### KUBOTA Store Commission ###
        inv_kubota_store_commission = models.execute_kw(db, uid,password, 'account.move' , 'create' ,[{
                        'date' : v_invoice_date,
                        'invoice_date':v_invoice_date,
                        'partner_id': v_partner_id_skc,
                        'partner_shipping_id': v_partner_id_skc,
                        # 'x_address':v_partner_x_address_skc,
                        'team_id': v_team_id,
                        'ref': v_doc_ref,
                        'move_type': v_inv_move_type,
                        'invoice_origin': v_invoice_origin,
                        'invoice_payment_term_id': v_payment_term_id_immediate,
                        'journal_id': v_inv_journal_id,

                        'invoice_line_ids':[(0,0,{
                                            'product_id':l_product_kin_skc,
                                            'name':l_invskc_label,
                                            'account_id': l_inv_skc_account_id,
                                            'analytic_account_id': l_analytic_account_id,
                                            'quantity':l_quantity,
                                            'price_unit':price_so_kin_skc,
                                            # 'product_uom_id':l_product_uom_id,
                                            'tax_ids': [[6, 0, [l_tax_7incl]]]})]
                            }])
        # link document excel                
        models.execute_kw(db, uid, password, 'account.move', 'write', [inv_kubota_store_commission, {'narration': doc_transaction}])                      
        print("KUBOTA Store Commission = ",inv_kubota_store_commission)


        ### KUBOTA Vendor Bill SKC ####
        vendor_bill_skc = models.execute_kw(db, uid,password, 'account.move' , 'create' ,[{
                        'date' : v_invoice_date,
                        'invoice_date':v_invoice_date,
                        'partner_id': v_partner_id_skc,
                        'partner_shipping_id':v_partner_id_skc,
                        'team_id': v_team_id,
                        'ref': v_doc_ref,
                        'move_type': v_vb_move_type,
                        'invoice_origin': v_invoice_origin,
                        'invoice_payment_term_id' : v_payment_term_id_standard,
                        'journal_id': v_vb_journal_id,

                        'invoice_line_ids':[(0,0,{
                                            'product_id':l_product_kin_cust,
                                            'name':l_vbskc_label,
                                            'account_id': l_susp_account_id,
                                            'analytic_account_id': l_analytic_account_id_none,
                                            'quantity':l_quantity,
                                            'price_unit':price_po_kin_skc,
                                            # 'product_uom_id':l_product_uom_id
                                            })]
                            }])
        # link document excel                
        models.execute_kw(db, uid, password, 'account.move', 'write', [vendor_bill_skc, {'narration': doc_transaction}])                        
        print("Vendor Bill SKC = ",vendor_bill_skc)
        result = {'KUBOTA Store Invoice' :inv_kubota_store_customer ,'KUBOTA Store Commission':inv_kubota_store_commission,'Vendor Bill SKC':vendor_bill_skc}

    return result
    

            

