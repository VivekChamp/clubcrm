from __future__ import unicode_literals
import frappe
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def member_checkin(date,client_id,client_name,checkin_time):
    doc = frappe.get_doc({
        'doctype': 'Check In',
        'date': date,
        'client_id': client_id,
        'client_name': client_name,
        'check_in_time': checkin_time
    })
    doc.insert()
    doc.submit()
    frappe.response["message"] = {
        "Name": doc.name,
        "Status": 1,
        "Status Message":"Checked in successfully"
        }