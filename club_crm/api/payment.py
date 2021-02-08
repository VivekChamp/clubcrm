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

secret = frappe.db.get_value("CS Signature",None,"secret_key")

membership_application = "^MEM-APP-[0-9]{4,4}-[0-9]{5,5}$"
online_order = "^ON-[0-9]{3,3}$"
food_order = "^FOE-[0-9]{4,4}-[0-9]{5,5}$"
fitness_training = "^FIT-REQ-[0-9]{4,4}-[0-9]{5,5}$"
spa_app = "^SPA-APP-[0-9]{4,4}-[0-9]{5,5}$"

@frappe.whitelist(allow_guest = True)
def create_log(**kwargs):
    kwargs=frappe._dict(kwargs)
    # frappe.throw(str(response))
    doc = frappe.new_doc("Payment Logs")
    doc.transaction_time=now()
    doc.response_data=str(kwargs)
    doc.payment_gateway_hash = kwargs['signature']
    doc.transaction_id=kwargs['transaction_id']
    doc.decision=kwargs['decision']
    doc.req_access_key=kwargs['req_access_key']
    doc.req_profile_id=kwargs['req_profile_id']
    doc.req_transaction_uuid=kwargs['req_transaction_uuid']
    doc.req_transaction_type=kwargs['req_transaction_type']
    doc.req_reference_number=kwargs['req_reference_number']
    doc.req_amount=kwargs['req_amount']
    doc.req_currency=kwargs['req_currency']
    doc.req_locale=kwargs['req_locale']
    doc.req_payment_method=kwargs['req_payment_method']
    doc.req_payment_token=kwargs['req_payment_token']
    doc.req_card_number=kwargs['req_card_number']
    doc.req_card_type=kwargs['req_card_type']
    doc.card_type_name=kwargs['card_type_name']
    doc.message=kwargs['message']
    doc.reason_code=kwargs['reason_code']
    doc.auth_avs_code=kwargs['auth_avs_code']
    doc.auth_response=kwargs['auth_response']
    doc.auth_amount=kwargs['auth_amount']
    doc.auth_code=kwargs['auth_code']
    doc.auth_cavv_result=kwargs['auth_cavv_result']
    doc.auth_cavv_result_raw=kwargs['auth_cavv_result_raw']
    doc.auth_trans_ref_no=kwargs['auth_trans_ref_no']
    doc.auth_time=kwargs['auth_time']
    doc.request_token=kwargs['request_token']
    doc.bill_trans_ref_no=kwargs['bill_trans_ref_no']
    doc.signed_field_names=kwargs['signed_field_names']
    doc.signed_date_time=kwargs['signed_date_time']
    # doc.generated_hash = generate_hash(str(kwargs['signed_date_time']))
    signed_list = kwargs['signed_field_names'].split(",")
    sample_dict = {}
    for item in signed_list:
        sample_dict[item] = kwargs[item]
    # return sample_dict
    doc.generated_hash = generate_hash_varifier(sample_dict)
    if doc.generated_hash == kwargs['signature']:
        doc.signature_verified = 1
        make_status_paid(kwargs['req_reference_number'])
        

    doc.insert(ignore_permissions=True)
    return doc



def generate_data_string(data_dict):
    test_array = []
    for key,value in data_dict.items():
        test_array.append(str(key)+"="+str(value))

    str1 = ",".join(test_array)
    return str1

def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_lowercase + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

def generate_uuid():
    transaction_uuid = str(uuid.uuid4()).replace("-", "")
    return transaction_uuid

@frappe.whitelist(allow_guest = True)
def generate_hash(data_dict):
    default_dict = {
        #"transaction_uuid" : get_random_alphanumeric_string(13),
        "transaction_uuid": generate_uuid(),
        "signed_date_time" : generate_signed_time(),
        "locale":"en",
        "currency":"qar",
	    "payment_method":"card",
        "bill_to_address_country":"qa",
        "signed_field_names":"transaction_uuid,signed_date_time,locale,currency,payment_method,bill_to_address_country,signed_field_names,unsigned_field_names,access_key,profile_id,transaction_type,reference_number,amount,bill_to_forename,bill_to_surname,bill_to_email,bill_to_address_line1,bill_to_address_city",
        "unsigned_field_names":"card_number,card_type,card_expiry_date"
    }
    default_dict.update(data_dict)
    # return default_dict
    API_SECRET = frappe.db.get_value("CS Signature",None,"secret_key")
    hash_value = hmac.new(API_SECRET.encode(), generate_data_string(default_dict).encode(), hashlib.sha256)
    # print(hash_value.digest())
    signature = base64.b64encode(hash_value.digest()).decode("utf-8")
    default_dict['signature'] = signature
    
    return default_dict


@frappe.whitelist(allow_guest = True)
def generate_hash_varifier(data_dict):
   
    # return default_dict
    API_SECRET = frappe.db.get_value("CS Signature",None,"secret_key")
    hash_value = hmac.new(API_SECRET.encode(), generate_data_string(data_dict).encode(), hashlib.sha256)
    # print(hash_value.digest())
    signature = base64.b64encode(hash_value.digest()).decode("utf-8")
    
    return signature


def generate_signed_time():
    signed_date=datetime.utcnow().replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    return signed_date

def make_status_paid(docname):
    if re.match(membership_application, docname):
        frappe.db.set_value("Memberships Application",str(docname),"payment_status","Paid")
        doc = frappe.get_doc("Memberships Application",str(docname))
        doc.save()
        
    elif re.match(online_order, docname):
        frappe.db.set_value("Online Order",str(docname),"payment_status","Paid")
        doc = frappe.get_doc("Online Order",str(docname))
        doc.save()
        
    elif re.match(food_order, docname):
        frappe.db.set_value("Food Order Entry",str(docname),"payment_status","Paid")
        doc = frappe.get_doc("Food Order Entry",str(docname))
        doc.save()
        
    elif re.match(fitness_training, docname):
        frappe.db.set_value("Fitness Training Request",str(docname),"payment_status","Paid")
        doc = frappe.get_doc("Fitness Training Request",str(docname))
        doc.save()
        
    elif re.match(spa_app, docname):
        frappe.db.set_value("Spa Appointment",str(docname),"payment_status","Paid")
        doc = frappe.get_doc("Spa Appointment",str(docname))
        doc.save()