from __future__ import unicode_literals
import frappe
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def member_checkin(client_id):
    doc= frappe.get_doc('Client',client_id)
    if doc.membership_status=="Member":
        doc = frappe.get_doc({
        'doctype': 'Check In',
        'series': "CHK-.YYYY.-MEM.-",
        'client_id': client_id,
        'checkin_type': "Member Check-in"
        })
        doc.insert()
        doc.submit()
        frappe.response["message"] = {
            "Name": doc.name,
            "Status": 1,
            "Status Message":"Checked in successfully"
        }
    else:
        frappe.response["message"]={
            "Status":0,
            "Status Message": "Not a member"
        }