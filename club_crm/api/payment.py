import frappe
import re
from frappe.utils import now
import hashlib


@frappe.whitelist(allow_guest = True)
def create_log(**kwargs):
    kwargs=frappe._dict(kwargs)
    # frappe.throw(str(response))
    doc = frappe.new_doc("Payment Logs")
    doc.transaction_time=now()
    doc.response_data=str(kwargs)
    doc.transaction_id=kwargs['transaction_id']
    doc.decision=kwargs['decision']
    doc.req_access_key=kwargs['req_access_key']
    doc.req_profile_id=kwargs['req_profile_id']
    doc.req_transaction_uuid=kwargs['req_transaction_uuid']
    doc.req_transaction_type=kwargs['req_transaction_type']
    doc.req_reference_number=kwargs['req_reference_number']
    doc.req_amount=kwargs['req_amount']
    doc.req_currency=kwargs['req_currency']
    doc.req_currency=kwargs['req_currency']
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
    # doc.signed_field_names=kwargs['signed_field_names']
    doc.signed_date_time=kwargs['signed_date_time']
    doc.generated_hash = generate_hash(str(kwargs['signed_date_time']))
    doc.insert(ignore_permissions=True)
    return doc

def generate_hash(fields):
    raw_str = ""
    for item in fields:
        raw_str = raw_str + str(item)
    m = hashlib.sha256()
    m.update(bytes(raw_str,'utf-8'))
    return m.digest()

