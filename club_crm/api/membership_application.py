from __future__ import unicode_literals
import frappe
from frappe.utils import escape_html
from frappe.utils.file_manager import upload
from frappe import throw, msgprint, _

@frappe.whitelist()
def apply_single(client_id,membership_plan,qatar_id,nationality,occupation,company,front_qid_filedata,back_qid_filedata,how_did):
    doc = frappe.get_doc({
        'doctype': 'Memberships Application',
        'submitted_by_staff':0,
        'client_id': client_id,
        'membership_type': "Single Membership",
        'membership_plan': membership_plan,
        'qatar_id_1': qatar_id,
        'nationality_1': nationality,
        'occupation_1': occupation,
        'company_1': company,
        'how_did': how_did
        })
    doc.insert()
    upload_image(doc.name,"qid_front.jpg",1,front_qid_filedata)
    doc.front_qid_1 = ret.file_url
    upload_image(doc.name,"qid_back.jpg",1,back_qid_filedata)
    doc.back_qid_1= ret.file_url
    doc.save()

    frappe.db.set_value('Client',client_id,'apply_membership','1')
    frappe.db.set_value('Client',client_id,'mem_application',doc.name)
    frappe.db.commit()
    frappe.response["message"] = {
        "Status": 1,
        "Status Message":"Membership Application has been submitted",
        "Name": doc.name
        }

def upload_image(docname,filename,isprivate,filedata):
    global ret
    ret = frappe.get_doc({
        "doctype": "File",
        "attached_to_name": docname,
        "attached_to_doctype": "Memberships Application",
        "file_name": filename,
        "is_private": isprivate,
        "content": filedata,
        "decode": True
        })
    ret.save()
    return ret.file_url

@frappe.whitelist()
def check_status(mem_application):
    doc= frappe.get_doc('Memberships Application', mem_application)
    if doc.application_status=="Pending":
        frappe.response["message"] = {
            "status": 0,
            "status_message":"Pending approval"
            }
    elif doc.application_status=="Rejected":
        frappe.response["message"] = {
            "status": 2,
            "status_message":"Rejected",
            "reason": doc.notes
            }
    elif doc.application_status=="Approved":
        if doc.payment_status=="Not Paid":
            frappe.response["message"] = {
                "status": 1,
                "status_message":"Approved. Pending Payment",
                "total_amount": doc.grand_total
                }
        else:
            frappe.response["message"] = {
                "status": 3,
                "status_message":"Please wait while you membership is activated",
                }
