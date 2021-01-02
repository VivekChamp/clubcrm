import frappe
import datetime
import time
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta
from frappe.utils import escape_html
from frappe import throw, msgprint, _
from club_crm.api.wallet import get_balance

@frappe.whitelist()
def get_spa_category(client_id):
    spa_category = frappe.get_all('Spa Menu Category', filters={'on_app': '1', 'complimentary':'0'}, fields=['spa_category_name','category_image'])

    client= frappe.get_doc('Client', client_id)
    if client.membership_status=="Member":
        mem= frappe.get_list('Member Benefits', filters={'client_id':client_id, 'benefit_status':'Active'}, fields=['*'])
        if mem:
            for d in mem:
                ben= frappe.get_doc('Member Benefits', d.name)
                spa= []
                for t in ben.benefits:
                    if t.type=="Spa" and t.remaining!='0':
                        spa.append(t)
                    else:
                        frappe.response["message"] = {
                            "Spa Categories": spa_category
                        }
                for x in spa:
                    spa_mem_category = frappe.get_all('Spa Menu Category', filters={'on_app': '1'}, fields=['spa_category_name','category_image'])
                    frappe.response["message"] = {
                        "Spa Categories": spa_mem_category
                    }
        else:
            frappe.response["message"] = {
                "Spa Categories": spa_category
            }
    else:
        frappe.response["message"] = {
            "Spa Categories": spa_category
        }

@frappe.whitelist()
def get_spa_item(spa_category):
    spa_item = frappe.get_all('Spa Menu', filters={'spa_menu_category':spa_category,'on_app': 1,'disabled':0},fields=['spa_item_name','spa_menu_group','spa_menu_category','duration','rate','has_addon','description','image'])
    frappe.response["message"] = {
        "Spa Items": spa_item
        }

@frappe.whitelist()
def get_therapist(spa_item,client_id):
    doc= frappe.get_doc('Spa Menu',spa_item)
    client= frappe.get_doc('Client', client_id)
    spa_therapist= frappe.get_all('Spa Therapist Assignment', filters={'spa_group':doc.spa_menu_group, 'on_app':1}, fields=['name','parent','parenttype','parentfield','spa_group'])
    therapist=[]
    for name in spa_therapist:
        doc_1= frappe.get_doc('Spa Therapist', name.parent)
        if doc_1.on_app==1:
            if client.membership_status=="Non-Member":
                if doc_1.gender==client.gender:
                    therapist.append({
                        'Document Name': doc_1.name,
                        'Therapist Name': doc_1.employee_name,
                        'Gender': doc_1.gender
                        })
            else:
                therapist.append({
                    'Document Name': doc_1.name,
                    'Therapist Name': doc_1.employee_name,
                    'Gender': doc_1.gender
                    })
    return therapist

@frappe.whitelist()
def get_details(client_id):
    time=frappe.get_doc('Club Settings')
    if time.spa_cancel_time and int(time.spa_cancel_time) >0:
        b= int(int(time.spa_cancel_time)/3600)

    doc = frappe.get_all('Spa Appointment', filters={'client_id':client_id, 'status':['not in',{'Cancelled','No Show'}]}, fields=['name','spa_item','duration','status','payment_status','appointment_date','appointment_time', 'start_time','rate','spa_therapist'])
    details=[]
    if doc:
        for rating in doc:
            rate=frappe.get_all('Rating', filters={'document_id':rating.name}, fields=['rating_point'])
            cancel_time= rating.start_time - timedelta(seconds=int(time.spa_cancel_time))
            if rate:
                rate=rate[0]
                details.append({
                    'Spa Appointment': {
                        "name": rating.name,
                        "spa_item": rating.spa_item,
                        "duration": int(rating.duration),
                        "status": rating.status,
                        "payment_status": rating.payment_status,
                        "appointment_date": rating.appointment_date,
                        "appointment_time": rating.appointment_time,
                        "start_time": rating.start_time,
                        "rate": str(rating.rate),
                        "therapist_name": rating.spa_therapist
                    },
                    'Rating': rate.rating_point,
                    'cancellation_time': cancel_time
                    })
            else:
                details.append({
                    'Spa Appointment': {
                        "name": rating.name,
                        "spa_item": rating.spa_item,
                        "duration": int(rating.duration),
                        "status": rating.status,
                        "payment_status": rating.payment_status,
                        "appointment_date": rating.appointment_date,
                        "appointment_time": rating.appointment_time,
                        "start_time": rating.start_time,
                        "rate": str(rating.rate),
                        "therapist_name": rating.spa_therapist
                    },
                    'Rating': -1,
                    'cancellation_time': cancel_time
                    })
        return details      

@frappe.whitelist()
def book_spa(client_id, spa_item, therapist_name, date, time,any_surgeries,payment_method):
    doc = frappe.get_doc({
        'doctype': 'Spa Appointment',
        'online': '1',
        'client_id': client_id,
        'spa_item': spa_item,
        'status': "Draft",
        'spa_therapist': therapist_name,
        'appointment_date': date,
        'appointment_time': time,
        'any_surgeries': any_surgeries,
        'payment_method': payment_method
        })
    doc.insert()
    wallet= get_balance(client_id)
    frappe.response["message"] = {
        "status": 1,
        "status_message": "Spa booking created successfully",
        "document_name": doc.name,
        "appointment_status": doc.status,
        "payment_status": doc.payment_status,
        "client_name": doc.client_name,
        "spa_item": doc.spa_item,
        "duration": doc.duration,
        "rate": doc.rate,
        "spa_therapist": doc.spa_therapist,
        "appointment_date": doc.appointment_date,
        "appointment_time": doc.appointment_time,
        "wallet_balance": wallet
        }

@frappe.whitelist()
def get_room(gender):
    doc= frappe.get_all('Club Room', filters={'is_group':0, 'for_gender':gender})
    return doc


@frappe.whitelist()
def get_slots(date, spa_item, therapist_name):
    doc = frappe.get_doc('Spa Menu', spa_item)

    # Find the number of 30 minutes interval in the total duration of spa menu. Total duration is in seconds.
    b= int(doc.total_duration/1800)

    # Fetch the day from date
    day_name= ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    weekday= day_name[datetime.strptime(str(date), '%Y-%m-%d').weekday()]

    # Fetch therapist schedule from therapist name
    therapist_doc = frappe.get_doc('Spa Therapist', therapist_name)
    if therapist_doc.spa_therapist_schedule:
        for d in therapist_doc.spa_therapist_schedule:
            therapist_schedule= frappe.get_doc('Spa Schedule', d.schedule)
            if therapist_schedule:
                time_slot=[]
                for t in therapist_schedule.time_slots:
                    if t.day==weekday:
                        time_slot.append(t.from_time)
                
                # Check for existing appointments and remove the appointment times from time slots
                appointments = frappe.get_all('Spa Appointment', filters= {'spa_therapist': therapist_name, 'docstatus':'1', 'appointment_date': date,'status': ['in', {'Draft','Scheduled','Open'}]}, fields=['name','appointment_date','appointment_time','total_duration','spa_item','start_time','end_time','status'])
                if appointments:
                    for s in appointments:
                            for a in time_slot[:]:
                                slot_time= datetime.combine(getdate(s.appointment_date), get_time(a))
                                if s.start_time <= slot_time <= s.end_time:
                                    time_slot.remove(a)  

                    # Check for time slots fitting the duration of the selected treatment
                    slot= []
                    for i in range(len(time_slot) - b):
                        d=1
                        for j in range(i+1, i+b+1):
                            if time_slot[j] - time_slot[i] == timedelta(minutes = 30*d):  
                                d = d+1
                            if d>b:
                                slot.append(time_slot[i])
                    frappe.response["message"] = {
                        "available_slots": slot
                        }
                else:
                    slot= []
                    for i in range(len(time_slot) - b):
                        d=1
                        for j in range(i+1, i+b+1):
                            if time_slot[j] - time_slot[i] == timedelta(minutes = 30*d):  
                                d = d+1
                            if d>b:
                                slot.append(time_slot[i])
                    frappe.response["message"] = {
                        "available_slots": slot
                        }
            else:
                frappe.throw('No schedule assigned for this therapist')
    else:
        frappe.throw('No schedule assigned for this therapist')

@frappe.whitelist()
def cancel_spa(client_id,booking_id):
    doc= frappe.get_doc('Spa Appointment', booking_id)
    if doc and doc.client_id==client_id:
        doc.db_set('docstatus', 2)
        doc.reload()
        wallet= get_balance(client_id)
        frappe.response["message"] = {
            "status": 1,
            "status_message": "Spa booking cancelled",
            "document_name": doc.name,
            "wallet_balance": wallet
            }
    else:
        frappe.response["message"] = {
            "status": 0,
            "status_message": "Client and Booking ID mismatch",
            }
