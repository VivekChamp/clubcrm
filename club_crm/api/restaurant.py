from __future__ import unicode_literals
import frappe
import datetime
import time
from datetime import datetime, timedelta
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def reservation(client_id,no_of_people,date,start_time):
    dt= date+" "+start_time
    starttime = datetime.strptime(dt, "%d-%m-%Y %H:%M")
    endtime= starttime + timedelta(minutes=60)
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

@frappe.whitelist()         
def get_time(date):
    date_1=str(date)
    day_name= ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    day_1 = datetime.strptime(date_1, '%d-%m-%Y').weekday()
    day= day_name[day_1]

    doc= frappe.get_doc('Grams Schedule')
    slots = doc.time_slots
    time_slot=[]
    for days in slots:
        if days.day==day and days.disabled==0:
            time_slot.append(days.from_time)
    return time_slot

@frappe.whitelist()         
def cancel_reservation(client_id):
    doc= frappe.get_all('Grams Reservation', filters={'client_id':client_id,'status': ['in',{'Pending', 'Scheduled'}], 'docstatus':1})
    if doc:
        doc_1=doc[0]
        frappe.db.set_value('Grams Reservation', doc_1.name, {
            'docstatus': 2,
            'status': 'Cancelled'
            })
        frappe.response["message"] = {
            "status": 1,
            "status_message":"Table Reservation Cancelled"
            }