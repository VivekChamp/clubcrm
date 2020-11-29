import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_schedule():
    time_schedule = frappe.get_all('Club Tour Schedule')
    frappe.response["message"] = {
        "Preferred Time": time_schedule
         }

@frappe.whitelist()         
def get_status(client_id):
    doc= frappe.get_all('Club Tour', filters={'client_id':client_id,'tour_status': "Pending"}, fields=["*"])
    if doc:
        frappe.response["message"] = {
            "Status": 0,
            "Status Message": "Pending"
            }
    else:
        doc= frappe.get_all('Club Tour', filters={'client_id':client_id,'tour_status': "Scheduled"}, fields=["*"])
        if doc:
            doc_1= doc[0]
            frappe.response["message"] = {
            "Status":1,
            "Status Message": "Scheduled",
            "From Time": doc_1.start_time,
            "To Time": doc_1.end_time
            }

@frappe.whitelist()
def create_clubtour(client_id,date,time):
    doc= frappe.get_doc({
            'doctype': 'Club Tour',
            'client_id': client_id,
            'preferred_date': date,
            'preferred_time_between': time
            })
    doc.insert()
    frappe.response["message"] = {
            "Status":1,
            "Status Message": "Club Tour booking submitted"}
