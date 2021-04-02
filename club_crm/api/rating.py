from __future__ import unicode_literals
import frappe
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def spa_rating(client_id,booking_id,rating,comments):
    doc_all= frappe.get_list('Rating', filters={'document_id':booking_id, 'docstatus':1})
    if not doc_all:
        doc = frappe.get_doc({
        'doctype': 'Rating',
        'client_id': client_id,
        'rating_type': "Spa Appointment",
        'document_id': booking_id,
        'rating_point': int(rating),
        'comments': comments
        })
        doc.insert()
        doc.submit()
        frappe.response["message"] = {
        "Name": doc.name,
        "Status":1,
        "Status Message": "Rating submitted successfully"
        }
    else:
        frappe.response["message"] = {
        "Status":0,
        "Status Message": "Rating already done earlier"
        }

@frappe.whitelist()
def check_status(booking_id):
    doc= frappe.get_all('Rating', filters={'document_id':booking_id, 'docstatus':1}, fields=["*"])
    if not doc:
        frappe.response["message"] = {
        "Rating": -1
        }
    else:
        doc_1= doc[0]
        frappe.response["message"] = {
        "Rating":doc_1.rating_point
        }

@frappe.whitelist()
def groupclass_rating(client_id,class_id,rating,comments):
    doc_all= frappe.get_all('Rating', filters={'document_id':class_id, 'docstatus':1, 'client_id':client_id})
    if not doc_all:
        doc = frappe.get_doc({
        'doctype': 'Rating',
        'client_id': client_id,
        'rating_type': "Group Class",
        'document_id': class_id,
        'rating_point': int(rating),
        'comments': comments
        })
        doc.insert()
        doc.submit()
        frappe.response["message"] = {
        "Name": doc.name,
        "Status":1,
        "Status Message": "Rating submitted successfully"
        }
    else:
        frappe.response["message"] = {
        "Status":0,
        "Status Message": "Rating already done earlier"
        }

@frappe.whitelist()
def pt_rating(client_id,appointment_id,rating,comments):
    doc_all= frappe.get_list('Rating', filters={'document_id':appointment_id, 'docstatus':1})
    if not doc_all:
        doc = frappe.get_doc({
        'doctype': 'Rating',
        'client_id': client_id,
        'rating_type': "Fitness Training Appointment",
        'document_id': appointment_id,
        'rating_point': int(rating),
        'comments': comments
        })
        doc.insert()
        doc.submit()
        frappe.response["message"] = {
        "Name": doc.name,
        "status":1,
        "status_message": "Rating submitted successfully"
        }
    else:
        frappe.response["message"] = {
        "status":0,
        "status_message": "Rating already done earlier"
        }