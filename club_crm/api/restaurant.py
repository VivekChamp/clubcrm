from __future__ import unicode_literals
import frappe
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def reservation(client_id,no_of_people,date,start_time,end_time):
    starttime= date+" "+start_time
    endtime= date+" "+end_time
    doc = frappe.get_doc({
        'doctype': 'Grams Reservation',
        'client_id': client_id,
        'status': 'Pending',
        'no_of_people':no_of_people,
        'reservation_time': starttime,
        'reservation_end_time': endtime
        })
    doc.insert()
    doc.submit()
    frappe.response["message"] = {
        "Name": doc.name,
        "Status":1,
        "Status Message": "Reservation submitted successfully"
        }

@frappe.whitelist()         
def get_status(client_id):
    doc= frappe.get_all('Grams Reservation', filters={'client_id':client_id,'status': "Pending"}, fields=["*"])
    if doc:
        frappe.response["message"] = {
            "Status": 0,
            "Status Message": "Pending"
            }
    else:
        doc= frappe.get_all('Grams Reservation', filters={'client_id':client_id,'status': "Scheduled"}, fields=["*"])
        if doc:
            doc_1= doc[0]
            frappe.response["message"] = {
            "Status":1,
            "Status Message": "Scheduled",
            "From Time": doc_1.reservation_time,
            "To Time": doc_1.reservation_end_time
            }