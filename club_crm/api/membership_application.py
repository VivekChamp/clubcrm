from __future__ import unicode_literals
import frappe
from frappe.utils import escape_html
from frappe.utils.file_manager import upload
from frappe import throw, msgprint, _

@frappe.whitelist()
def apply_single(date,client_id,membership_plan,qatar_id,nationality,occupation,company,front_qid_filedata,back_qid_filedata):
    doc = frappe.get_doc({
        'doctype': 'Memberships Application',
        'submitted_by_staff':0,
        'date': date,
        'client_id': client_id,
        'membership_type': "Single Membership",
        'membership_plan': membership_plan,
        'qatar_id_1': qatar_id,
        'nationality_1': nationality,
        'occupation_1': occupation,
        'company_1': company
        })
    doc.insert()
    title=doc.get_title()
    docs= frappe.get_doc('Memberships Application',title)

    upload_image(title,"qid_front.jpg",1,front_qid_filedata)
    docs.front_qid_1 = ret1.file_url

    upload_image(title,"qid_back.jpg",1,back_qid_filedata)
    docs.back_qid_1= ret1.file_url

    docs.save()

    frappe.db.set_value('Memberships Application', title, 'application_status', "Pending")
    frappe.db.set_value('Client',client_id,'apply_membership',1)
    frappe.db.set_value('Client',client_id,'mem_application',title)
    frappe.response["message"] = {
        "Name": title,
        "Status":"Membership Application has been submitted"
        }

def upload_image(docname,filename,isprivate,filedata):
    global ret1
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
    ret1= frappe.get_last_doc('File')
    return ret1.file_url

@frappe.whitelist()
def check_status(mem_application):
    application = frappe.get_doc('Memberships Application', mem_application)
    if application.application_status=="Pending":
        frappe.response["message"] = "Pending approval"
    elif application.application_status=="Rejected":
        frappe.response["message"] = "Rejected"
    elif application.application_status=="Approved":
        if application.payment_status=="Not Paid":
            frappe.response["message"] = "Approved. Pending Payment"
        else:
            frappe.response["message"] = "You are a member. Please login again to reflect your changes"
