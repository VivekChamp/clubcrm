import frappe
import re
import uuid
from frappe.utils import now
import hashlib
import hmac
import hashlib
import base64 
from datetime import datetime
import random
import string

@frappe.whitelist(allow_guest = True)
def create_log(**kwargs):
    kwargs=frappe._dict(kwargs)

    doc = frappe.new_doc("Payment Log")
    doc.date_time=now()
    doc.response_data=str(kwargs)
    doc.payment_gateway_hash = kwargs['signature']
    doc.decision=kwargs['decision']
    doc.transaction_id=kwargs['auth_trans_ref_no']
    doc.req_transaction_uuid=kwargs['req_transaction_uuid']
    doc.req_transaction_type=kwargs['req_transaction_type']
    doc.req_reference_number=kwargs['req_reference_number']
    doc.req_amount=kwargs['req_amount']
    doc.req_bill_to_forename=kwargs['req_bill_to_forename']
    doc.req_bill_to_surname=kwargs['req_bill_to_surname']
    doc.req_customer_ip_address=kwargs['req_customer_ip_address']
    doc.req_card_number=kwargs['req_card_number']
    doc.card_type_name=kwargs['card_type_name']
    doc.message=kwargs['message']
    doc.reason_code=kwargs['reason_code']
    doc.auth_amount=kwargs['auth_amount']
    doc.signed_field_names=kwargs['signed_field_names']
    doc.signed_date_time=kwargs['signed_date_time']

    signed_list = kwargs['signed_field_names'].split(",")
    sample_dict = {}
    for item in signed_list:
        sample_dict[item] = kwargs[item]

    doc.generated_hash = generate_hash_verifier(sample_dict)
    if doc.generated_hash == kwargs['signature']:
        doc.signature_verified = 1

    doc.insert(ignore_permissions=True)
    return doc

def generate_data_string(data_dict):
    test_array = []
    for key,value in data_dict.items():
        test_array.append(str(key)+"="+str(value))

    str1 = ",".join(test_array)
    return str1

def generate_uuid():
    transaction_uuid = str(uuid.uuid4()).replace("-", "")
    return transaction_uuid

def customer_ip():
    user = frappe.get_doc('User', frappe.session.user)
    customer_ip = user.last_ip
    return customer_ip

def generate_hash_verifier(data_dict):
    API_SECRET = frappe.db.get_value("CS Signature",None,"secret_key")
    hash_value = hmac.new(API_SECRET.encode(), generate_data_string(data_dict).encode(), hashlib.sha256)
    # print(hash_value.digest())
    signature = base64.b64encode(hash_value.digest()).decode("utf-8")  
    return signature

def generate_signed_time():
    signed_date=datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    return signed_date

@frappe.whitelist()
def generate_hash(data_dict):
    user = frappe.get_doc('User', frappe.session.user)
    access_key = frappe.db.get_value("CS Settings",None,"access_key")
    profile_id = frappe.db.get_value("CS Settings",None,"profile_id")
    default_dict = {
        "access_key": access_key,
        "profile_id": profile_id,
        'customer_ip_address': customer_ip(),
        "device_fingerprint_id": generate_uuid(),
        "transaction_uuid": generate_uuid(),
        "signed_date_time" : generate_signed_time(),
        "locale":"en",
        "currency":"qar",
	    "payment_method":"card",
        "bill_to_forename": user.first_name,
        "bill_to_surname": user.last_name,
        "bill_to_email": frappe.session.user,
        "bill_to_address_country":"QA",
        "signed_field_names":"access_key,profile_id,transaction_uuid,customer_ip_address,device_fingerprint_id,signed_date_time,locale,transaction_type,signed_field_names,unsigned_field_names,reference_number,amount,currency,payment_method,bill_to_forename,bill_to_surname,bill_to_email,bill_to_address_country",
        "unsigned_field_names":""
    }
    default_dict.update(data_dict)
    signed_list = default_dict["signed_field_names"].split(",")
    test_array = []
    for item in signed_list:
        for key,value in default_dict.items():
            if key==item:
                test_array.append(str(key)+"="+str(value))
    
    str1 = ",".join(test_array)

    API_SECRET = frappe.db.get_value("CS Signature",None,"secret_key")

    hash_value = hmac.new(API_SECRET.encode(), str1.encode(), hashlib.sha256)
    # print(hash_value.digest())
    signature = base64.b64encode(hash_value.digest()).decode("utf-8")
    default_dict['signature'] = signature  

    # trial = []
    # for key,value in default_dict.items():
    #     trial.append(str(key)+"="+str(value))
    # return trial

    return default_dict