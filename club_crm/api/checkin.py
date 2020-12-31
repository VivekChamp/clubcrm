from __future__ import unicode_literals
import frappe
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def member_checkin(client_id):
    doc= frappe.get_doc('Client',client_id)
    if doc.membership_status=="Member":
        d = frappe.get_doc({
        'doctype': 'Check In',
        'series': "CHK-.YYYY.-MEM.-",
        'client_id': client_id,
        'check_in_type': "Member Check-in"
        })
        d.insert()
        d.submit()
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

@frappe.whitelist()
def spa_checkin(booking_id, client_id):
    d = frappe.get_doc({
        'doctype': 'Check In',
        'series': "CHK-.YYYY.-SPA.-",
        'client_id': client_id,
        'check_in_type': "Spa",
        'spa_booking': booking_id
        })
    d.insert()
    d.submit()
    frappe.response["message"] = {
        "Name": d.name,
        "Status": 1,
        "Status Message":"Checked in successfully"
    }

@frappe.whitelist()
def fitness_checkin(booking_id, client_id):
    d = frappe.get_doc({
        'doctype': 'Check In',
        'series': "CHK-.YYYY.-GYM.-",
        'client_id': client_id,
        'check_in_type': "Gym",
        'gym_booking': booking_id
        })
    d.insert()
    d.submit()
    frappe.response["message"] = {
        "Name": d.name,
        "Status": 1,
        "Status Message":"Checked in successfully"
    }

@frappe.whitelist()
def gc_checkin(booking_id, client_id):
    d = frappe.get_doc({
        'doctype': 'Check In',
        'series': "CHK-.YYYY.-GC.-",
        'client_id': client_id,
        'check_in_type': "Group Class",
        'class_attendee_id': booking_id
        })
    d.insert()
    d.submit()
    frappe.response["message"] = {
        "Name": d.name,
        "Status": 1,
        "Status Message":"Checked in successfully"
    }