from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime, timedelta, date, time
from frappe.utils import getdate, get_time, flt, now_datetime
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_schedule():
    time_schedule = frappe.get_doc('Club Settings')
    schedule = []
    for time in time_schedule.club_tour_schedule:
        from_time_string = str(time.from_time)
        from_time_datetime = datetime.strptime(from_time_string, "%H:%M:%S")
        from_time = datetime.strftime(from_time_datetime, "%I:%M %p")

        to_time_string = str(time.to_time)
        to_time_datetime = datetime.strptime(to_time_string, "%H:%M:%S")
        to_time = datetime.strftime(to_time_datetime, "%I:%M %p")

        name = _('{0} - {1}').format(from_time, to_time)
        schedule.append({
            "name" : name
        })     
      
    frappe.response["message"] = {
        "Preferred Time": schedule
    }


@frappe.whitelist()         
def get_status(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc= frappe.get_all('Club Tour', filters={'client_id':client.name,'tour_status': "Pending"}, fields=["*"])
    if doc:
        frappe.response["message"] = {
            "Status": 0,
            "Status Message": "Pending"
        }
    else:
        doc= frappe.get_all('Club Tour', filters={'client_id':client.name,'tour_status': "Scheduled"}, fields=["*"])
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
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_doc({
        'doctype': 'Club Tour',
        'client_id': client.name,
        'preferred_date': date,
        'preferred_time_between': time
        })
    doc.save()
    frappe.response["message"] = {
            "Status":1,
            "Status Message": "Club Tour booking submitted"
        }
