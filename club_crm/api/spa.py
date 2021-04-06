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
    spa_category = frappe.get_all('Spa Services Category', filters={'on_app': '1', 'complimentary':'0'}, fields=['spa_category_name','category_image'])
    # client= frappe.get_doc('Client', client_id)
    # if client.membership_status=="Member":
    #     mem= frappe.get_list('Member Benefits', filters={'client_id':client_id, 'benefit_status':'Active'}, fields=['*'])
    #     if mem:
    #         for d in mem:
    #             ben= frappe.get_doc('Member Benefits', d.name)
    #             spa= []
    #             for t in ben.benefits:
    #                 if t.type=="Spa" and t.remaining!='0':
    #                     spa.append(t)
    #                 else:
    #                     frappe.response["message"] = {
    #                         "Spa Categories": spa_category
    #                     }
    #             for x in spa:
    #                 spa_mem_category = frappe.get_all('Spa Services Category', filters={'on_app': '1'}, fields=['spa_category_name','category_image'])
    #                 frappe.response["message"] = {
    #                     "Spa Categories": spa_mem_category
    #                 }
    #     else:
    #         frappe.response["message"] = {
    #             "Spa Categories": spa_category
    #         }
    
    frappe.response["message"] = {
            "Spa Categories": spa_category
        }

@frappe.whitelist()
def get_spa_item(spa_category):
    spa = frappe.get_all('Spa Services', filters={'spa_category':spa_category,'on_app': 1,'enabled':1},fields=['spa_name','spa_group','spa_category','duration','price','description','image'])
    spa_item = []
    for item in spa:
        spa_item.append({
            "spa_item_name" : item.spa_name,
            "spa_menu_group" : item.spa_group,
            "spa_menu_category" : item.spa_category,
            "duration" : item.duration,
            "has_addon" : 0,
            "rate" : item.price,
            "description" : item.description,
            "image" : item.image
        })
    frappe.response["message"] = {
        "Spa Items": spa_item
        }

@frappe.whitelist()
def get_therapist(spa_item, client_id):
    spa = frappe.get_doc('Spa Services', spa_item)
    client = frappe.get_doc('Client', client_id)
    spa_therapists = frappe.get_all('Spa Services Assignment', filters={'spa_group':spa.spa_group, 'on_app':1}, fields=['name','parent','parenttype','parentfield','spa_group'])

    therapist=[]
    for name in spa_therapists:
        staff = frappe.get_doc('Service Staff', name.parent)
        if staff.on_app == 1:
            if client.membership_status == "Non-Member":
                if staff.gender == client.gender:
                    therapist.append({
                        'Document Name': staff.name,
                        'Therapist Name': staff.display_name,
                        'Gender': staff.gender
                        })
            else:
                therapist.append({
                    'Document Name': staff.name,
                    'Therapist Name': staff.display_name,
                    'Gender': staff.gender
                    })
    return therapist

@frappe.whitelist()
def get_details(client_id):
    time = frappe.get_doc('Club Settings')
    if time.spa_cancel_time and int(time.spa_cancel_time) > 0:
        b = int(int(time.spa_cancel_time)/3600)

    doc = frappe.get_all('Spa Appointment', filters={'client_id':client_id, 'appointment_status':['not in',{'Cancelled','No Show'}]}, fields=['name','spa_service','total_service_duration','appointment_status','payment_status','appointment_date','appointment_time', 'start_time','default_price','spa_therapist'], order_by="appointment_date asc")
    details = []
    if doc:
        for rating in doc:
            rate = frappe.get_all('Rating', filters={'document_id':rating.name}, fields=['rating_point'])
            cancel_time = rating.start_time - timedelta(seconds=int(time.spa_cancel_time))
            if rate:
                rate=rate[0]
                details.append({
                    'Spa Appointment': {
                        "name": rating.name,
                        "spa_item": rating.spa_service,
                        "duration": int(rating.total_service_duration),
                        "status": rating.appointment_status,
                        "payment_status": rating.payment_status,
                        "appointment_date": rating.appointment_date,
                        "appointment_time": rating.appointment_time,
                        "start_time": rating.start_time,
                        "rate": str(rating.default_price),
                        "therapist_name": rating.spa_therapist
                    },
                    'Rating': rate.rating_point,
                    'cancellation_time': cancel_time
                    })
            else:
                details.append({
                    'Spa Appointment': {
                        "name": rating.name,
                        "spa_item": rating.spa_service,
                        "duration": int(rating.total_service_duration),
                        "status": rating.appointment_status,
                        "payment_status": rating.payment_status,
                        "appointment_date": rating.appointment_date,
                        "appointment_time": rating.appointment_time,
                        "start_time": rating.start_time,
                        "rate": str(rating.default_price),
                        "therapist_name": rating.spa_therapist
                    },
                    'Rating': -1,
                    'cancellation_time': cancel_time
                    })
        return details      

@frappe.whitelist()
def book_spa(client_id, spa_item, therapist_name, date, time, any_surgeries,payment_method):
    start_time = datetime.combine(getdate(date), get_time(time))
    doc = frappe.get_doc({
        'doctype': 'Spa Appointment',
        'online': '1',
        'client_id': client_id,
        'spa_service': spa_item,
        'appointment_status': "Draft",
        'spa_therapist': therapist_name,
        'start_time': start_time,
        'any_surgeries': any_surgeries,
        'payment_method': payment_method
        })
    doc.insert()
    wallet= get_balance(client_id)
    frappe.response["message"] = {
        "status": 1,
        "status_message": "Spa booking created successfully",
        "document_name": doc.name,
        "appointment_status": doc.appointment_status,
        "payment_status": doc.payment_status,
        "client_name": doc.client_name,
        "spa_item": doc.spa_service,
        "duration": doc.service_duration,
        "rate": doc.default_price,
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
    doc = frappe.get_doc('Spa Services', spa_item)

    # date_converted = datetime.strptime(date,"%Y-%m-%d")
    date_converted = getdate(date)
    month = datetime.strftime(date_converted, "%m")
    year = datetime.strftime(date_converted, "%Y")
    # date_string = datetime.strftime(date_original, "%Y-%m-%d")
    

    # Fetch therapist schedule from therapist name
    staff_availability = frappe.get_all('Service Staff Availability', filters={'staff_name': therapist_name,  'month': month, 'year': year})
    if staff_availability:
        for staff in staff_availability:
            therapist_schedule = frappe.get_doc('Service Staff Availability', staff.name)

            time_slot = []
            for availability in therapist_schedule.week_1:
                if availability.date == date_converted:
                    time_slot.append(availability.from_time)
                    while availability.from_time < availability.to_time:
                        availability.from_time += timedelta(minutes = 15)
                        time_slot.append(availability.from_time)
            for availability in therapist_schedule.week_2:
                if availability.date == date_converted:
                    time_slot.append(availability.from_time)
                    while availability.from_time < availability.to_time:
                        availability.from_time += timedelta(minutes = 15)
                        time_slot.append(availability.from_time)
            for availability in therapist_schedule.week_3:
                if availability.date == date_converted:
                    time_slot.append(availability.from_time)
                    while availability.from_time < availability.to_time:
                        availability.from_time += timedelta(minutes = 15)
                        time_slot.append(availability.from_time)
            for availability in therapist_schedule.week_4:
                if availability.date == date_converted:
                    time_slot.append(availability.from_time)
                    while availability.from_time < availability.to_time:
                        availability.from_time += timedelta(minutes = 15)
                        time_slot.append(availability.from_time)
            for availability in therapist_schedule.week_5:
                if availability.date == date_converted:
                    time_slot.append(availability.from_time)
                    while availability.from_time < availability.to_time:
                        availability.from_time += timedelta(minutes = 15)
                        time_slot.append(availability.from_time)
            for availability in therapist_schedule.week_6:
                if availability.date == date_converted:
                    time_slot.append(availability.from_time)
                    while availability.from_time < availability.to_time:
                        availability.from_time += timedelta(minutes = 15)
                        time_slot.append(availability.from_time)
        if time_slot==[]:
            frappe.throw('No schedule assigned for this therapist')

        # Find the number of 30 minutes interval in the total duration of spa service. Total duration is in seconds.
        b = int(doc.total_duration/900)
                    
        # Check for existing appointments and remove the appointment times from time slots
        appointments = frappe.get_all('Spa Appointment', filters= {'spa_therapist': therapist_name, 'appointment_date': date_converted,'appointment_status': ['in', {'Draft','Scheduled','Open'}]}, fields=['name','appointment_date','appointment_time','total_duration','spa_service','start_time','end_time','appointment_status'])
        if appointments:
            for s in appointments:
                for a in time_slot[:]:
                    slot_time = datetime.combine(getdate(s.appointment_date), get_time(a))
                    if s.start_time <= slot_time <= s.end_time:
                        time_slot.remove(a)  

                # Check for time slots fitting the duration of the selected treatment
                slot= []
                for i in range(len(time_slot) - b):
                    d=1
                    for j in range(i+1, i+b+1):
                        if time_slot[j] - time_slot[i] == timedelta(minutes = 15*d):  
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
                    if time_slot[j] - time_slot[i] == timedelta(minutes = 15*d):  
                        d = d+1
                        if d>b:
                            slot.append(time_slot[i])
                frappe.response["message"] = {
                    "available_slots": slot
                }
    else:
        frappe.throw('No schedule assigned for this therapist')

@frappe.whitelist()
def cancel_spa(client_id,booking_id):
    doc= frappe.get_doc('Spa Appointment', booking_id)
    if doc and doc.client_id==client_id:
        doc.db_set('appointment_status', 'Cancelled')
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
