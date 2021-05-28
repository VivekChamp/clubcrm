import frappe
import datetime
import time
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta
from frappe.utils import escape_html
from frappe import throw, msgprint, _
from club_crm.api.wallet import get_balance
from club_crm.club_crm.doctype.cart.cart import add_cart_from_spa_online
from club_crm.club_crm.doctype.spa_appointment.spa_appointment import cancel_appointment

@frappe.whitelist()
def get_spa_category(client_id):
    spa_category = frappe.get_all('Spa Services Category', filters={'on_app': '1', 'complimentary':'0'}, fields=['spa_category_name','category_image'])
    frappe.response["message"] = {
            "Spa Categories": spa_category
        }

@frappe.whitelist()
def get_spa_item(spa_category):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_doc('Client', client.name)
    spa = frappe.get_all('Spa Services', filters={'spa_category':spa_category,'on_app': 1,'enabled':1,'session_type':'Single'}, fields=['spa_name','spa_group','spa_category','duration','price','description','image','gender_preference','no_member_discount'])
    spa_item = []

    discount = 0.0
    mem_discount = 0.0
    if doc.membership_status == "Member":
        if doc.membership_history:
            for row in doc.membership_history:
                if row.status == "Active":
                    mem = frappe.get_doc('Memberships', row.membership)
                    mem_discount = mem.spa_discount

        benefits = frappe.get_all('Client Sessions', filters={'client_id': doc.name, 'is_benefit': 1, 'session_status': 'Active','service_type': 'Spa Services'}, fields=['name','service_name'])
        if benefits:
            spa_comp = frappe.get_all('Spa Services', filters={'spa_category':spa_category,'enabled':1,'session_type':'Complimentary'}, fields=['spa_name','spa_group','spa_category','duration','price','description','image','gender_preference'])

            for benefit in benefits:
                for items in spa_comp:
                    if benefit.service_name == items.spa_name:
                        spa_item.append({
                            "spa_item_name" : items.spa_name,
                            "spa_menu_group" : items.spa_group,
                            "spa_menu_category" : items.spa_category,
                            "duration" : items.duration,
                            "has_addon" : 0,
                            "rate" : items.price,
                            "description" : items.description,
                            "image" : items.image
                        })

    for item in spa:
        discount = mem_discount
        if item.no_member_discount == 1:
            discount = 0.0
        discount_price = item.price - (item.price * (discount/100.0))
        price = discount_price//0.5*0.5
        if item.gender_preference == doc.gender or item.gender_preference == "No Preference" or not item.gender_preference:
            spa_item.append({
                "spa_item_name" : item.spa_name,
                "spa_menu_group" : item.spa_group,
                "spa_menu_category" : item.spa_category,
                "duration" : item.duration,
                "has_addon" : 0,
                "rate" : price,
                "description" : item.description,
                "image" : item.image
            })

    frappe.response["message"] = {
        "Spa Items": spa_item
    }

@frappe.whitelist()
def get_therapist(spa_item, client_id):
    spa = frappe.get_doc('Spa Services', spa_item)
    client = frappe.db.get("Client", {"email": frappe.session.user})
    # client = frappe.get_doc('Client', client_id)
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
                if client.gender == "Female":
                    if staff.gender == "Female":
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
    client = frappe.db.get("Client", {"email": frappe.session.user})
    time = frappe.get_doc('Spa Settings')
    if time.spa_cancellation_time and int(time.spa_cancellation_time) > 0:
        b = int(int(time.spa_cancellation_time)/3600)

    spa_list = frappe.get_all('Spa Appointment', filters={'client_id':client.name, 'appointment_status':['not in',{'Cancelled','No Show'}]}, fields=['name', 'appointment_date'], order_by="appointment_date asc")
    details = []
    if spa_list:
        for spa in spa_list:
            spa_doc = frappe.get_doc('Spa Appointment', spa.name)
            cancel_time = spa_doc.start_time - timedelta(seconds=int(time.spa_cancellation_time))
            if spa_doc.cart:
                cart_doc = frappe.get_doc('Cart', spa_doc.cart)
                rating_list = frappe.get_all('Rating', filters={'document_id': spa.name}, fields=['rating_point'])
                if rating_list:
                    for rating in rating_list:
                        details.append({
                            'Spa Appointment': {
                                "name": cart_doc.name,
                                "spa_item": spa_doc.spa_service,
                                "duration": int(spa_doc.service_duration),
                                "status": spa_doc.appointment_status,
                                "payment_status": spa_doc.payment_status,
                                "appointment_date": spa_doc.appointment_date,
                                "appointment_time": spa_doc.appointment_time,
                                "start_time": spa_doc.start_time,
                                "rate": cart_doc.grand_total,
                                "therapist_name": spa_doc.service_staff
                            },
                            'Rating': rating.rating_point,
                            'cancellation_time': cancel_time
                        })
                else:
                    details.append({
                    'Spa Appointment': {
                        "name": cart_doc.name,
                        "spa_item": spa_doc.spa_service,
                        "duration": int(spa_doc.service_duration),
                        "status": spa_doc.appointment_status,
                        "payment_status": spa_doc.payment_status,
                        "appointment_date": spa_doc.appointment_date,
                        "appointment_time": spa_doc.appointment_time,
                        "start_time": spa_doc.start_time,
                        "rate": cart_doc.grand_total,
                        "therapist_name": spa_doc.service_staff
                    },
                    'Rating': -1,
                    'cancellation_time': cancel_time
                    })
    return details

@frappe.whitelist()
def book_spa(client_id, spa_item, therapist_name, date, time, any_surgeries,payment_method):
    client = frappe.db.get("Client", {"email": frappe.session.user}) 
    start_time = datetime.combine(getdate(date), get_time(time))
    doc = frappe.get_doc({
        'doctype': 'Spa Appointment',
        'online': '1',
        'client_id': client.name,
        'spa_service': spa_item,
        'appointment_status': "Draft",
        'service_staff': therapist_name,
        'start_time': start_time,
        'any_surgeries': any_surgeries,
        'payment_method': payment_method
        })
    doc.save()
    cart = add_cart_from_spa_online(doc.client_id, doc.name)
    cart_doc = frappe.get_doc('Cart', cart)
    wallet= get_balance()
    frappe.response["message"] = {
        "status": 1,
        "status_message": "Spa booking created successfully",
        "document_name": cart,
        "appointment_status": doc.appointment_status,
        "payment_status": doc.payment_status,
        "client_name": doc.client_name,
        "spa_item": doc.spa_service,
        "duration": doc.service_duration,
        "rate": cart_doc.grand_total,
        "spa_therapist": doc.service_staff,
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

    date_converted = getdate(date)
    month = datetime.strftime(date_converted, "%m")
    year = datetime.strftime(date_converted, "%Y")
 
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
            frappe.response["message"] = {
                    "available_slots": []
                }

        # Find the number of 30 minutes interval in the total duration of spa service. Total duration is in seconds.
        b = int(doc.total_duration/900)
                    
        # Check for existing appointments and remove the appointment times from time slots
        appointments = frappe.get_all('Spa Appointment', filters= {'service_staff': therapist_name, 'appointment_date': date_converted,'appointment_status': ['in', {'Draft','Scheduled','Open'}]}, fields=['name','appointment_date','appointment_time','total_duration','spa_service','start_time','end_time','appointment_status'])
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

        # time_array = []
        # for one_time in slot[:]:
        #     one_time_datetime = datetime.strptime(str(one_time), "%H:%M:%S")
        #     one_time_ampm = datetime.strftime(one_time_datetime, "%I:%M %p")
        #     time_array.append(one_time_ampm)
        
        # frappe.response["message"] = {
        #             "available_slots": time_array
        # }

    else:
        frappe.response["message"] = {
                    "available_slots": []
                }

@frappe.whitelist()
def cancel_spa(client_id,booking_id):
    spa_list = frappe.get_all('Spa Appointment', filters={'cart': booking_id})
    if spa_list:
        for spa in spa_list:
            doc = frappe.get_doc('Spa Appointment', spa.name)
            if doc and doc.client_id==client_id:
                cancel_appointment(doc.name)
                # doc.db_set('appointment_status', 'Cancelled')
                # doc.db_set('docstatus', 2)
                # doc.reload()
                wallet= get_balance()
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

@frappe.whitelist()
def reschedule_spa(booking_id, date, time):
    spa_list = frappe.get_all('Spa Appointment', filters={'cart': booking_id})
    if spa_list:
        for spa in spa_list:
            doc = frappe.get_doc('Spa Appointment', spa.name)
            start_time = datetime.combine(getdate(date), get_time(time))
            doc.start_time = start_time
            doc.save()

            wallet= get_balance()
            frappe.response["message"] = {
                "status": 1,
                "status_message": "Spa booking rescheduled",
                "appointment_status": doc.appointment_status,
                "payment_status": doc.payment_status,
                "client_name": doc.client_name,
                "spa_item": doc.spa_service,
                "duration": doc.service_duration,
                "rate": doc.default_price,
                "spa_therapist": doc.service_staff,
                "appointment_date": doc.appointment_date,
                "appointment_time": doc.appointment_time,
                "wallet_balance": wallet
            }