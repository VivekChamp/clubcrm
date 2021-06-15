from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta, date, time
from frappe.utils import getdate, get_time, flt, now_datetime

@frappe.whitelist()
def member_checkin(client_id):
    client = frappe.get_doc('Client',client_id)
    if client.membership_status == "Member":
        doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id,
        'check_in_type': "Club Check-in"
        })
        doc.insert()
        doc.submit()

        frappe.response["message"] = {
            "Name": doc.name,
            "Status": 1,
            "Status Message":"Checked in successfully"
        }
    else:
        frappe.response["message"] = {
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

@frappe.whitelist()
def get_details(client_id):
    client = frappe.get_doc('Client', client_id)
    appointments = []

    # Fetch all the Open spa appointments of the client
    spa_list = frappe.get_all('Spa Appointment', filters={'client_id':client_id, 'appointment_status':'Open'}, fields=['name','spa_service','appointment_time','service_staff'])
    for spa in spa_list:
        appointments.append({
            "service_name": spa.spa_service,
            "service_staff" : spa.service_staff,
            "time": spa.appointment_time
        })

    # Fetch all the Open Group Classes of the client
    gc_list = frappe.get_all('Group Class Attendees', filters={'client_id':client_id,'class_status':'Open'}, fields=['name','group_class_name','from_time','trainer_name'])
    for gc in gc_list:
        appointments.append({
            "service_name": gc.group_class_name,
            "service_staff" : gc.trainer_name,
            "time": gc.from_time
        })

    # Fetch all the Open Fitness Training appointments of the client
    fitness_list = frappe.get_all('Fitness Training Appointment', filters={'client_id':client_id, 'appointment_status':'Open'}, fields=['name','fitness_service','appointment_time','service_staff'])
    for fitness in fitness_list:
        appointments.append({
            "service_name": fitness.fitness_service,
            "service_staff" : fitness.service_staff,
            "time": fitness.appointment_time
        })

    frappe.response["message"] = {
        "client_id": client_id,
        "full_name": client.client_name,
        "membership_status": client.membership_status,
        "image": client.image,
        "appointments" : appointments
    }

@frappe.whitelist()
def club_checkin(client_id):
    client = frappe.get_doc('Client', client_id)
    if client.status == "Disabled":
        frappe.throw('Disabled')
    else:
        doc = frappe.get_doc({
            'doctype': 'Check In',
            'client_id': client_id,
            'check_in_type': "Club Check-in",
            'checked_in_by' : 'Self Check-in'
            })
        doc.insert()
        doc.submit()
        
        client.status = "Checked-in"
        client.checkin_document = doc.name
        client.save()

        frappe.response["message"] = {
            "disabled": 0,
            "Name": doc.name,
            "Status": 1,
            "Status Message":"Checked in successfully"
        }

@frappe.whitelist(allow_guest=True)
def get_date_time():
    date_time = datetime.now()
    date = date_time.date()
    time = datetime.strftime(date_time, "%H:%M:%S")

    frappe.response["message"] = {
        'datetime': date_time,
        'date': date,
        'time': time
    }