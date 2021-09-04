import frappe
from datetime import date, time, datetime, timedelta
from frappe.utils import getdate, get_time, flt, now_datetime
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def package_requests():
    trainer = frappe.db.get("Service Staff", {"email": frappe.session.user})
    request_list = frappe.get_all('Fitness Training Request', filters={'trainer':trainer.name, 'request_status':['in',{'Scheduled','Pending'}]})

    requests = []
    for request in request_list:
        request_doc = frappe.get_doc('Fitness Training Request', request.name)

        if request_doc.request_status == "Pending":
            dates=[]
            for row in request_doc.customer_preference:
                dates.append({
                    'day': row.day,
                    'time': row.client_session
                })
            requests.append({
                'name': request_doc.name,
                'date': request_doc.date,
                'request_status': request_doc.request_status,
                'client_id': request_doc.client_id,
                'client_name': request_doc.client_name,
                'mobile_number':  request_doc.mobile_number,
                'gender':  request_doc.gender,
                'fitness_package':  request_doc.fitness_package,
                'no_of_sessions':  request_doc.number_of_sessions,
                'price':  request_doc.price,
                'start_day':  request_doc.start_date,
                'payment_status':  request_doc.payment_status,
                'customer_preference': dates
            })

        elif request_doc.request_status == "Scheduled":
            dates=[]
            for row in request_doc.table_schedule:
                dates.append({
                    'day': row.date,
                    'time': row.from_time
                })
            requests.append({
                'name': request_doc.name,
                'date': request_doc.date,
                'request_status': request_doc.request_status,
                'client_id': request_doc.client_id,
                'client_name': request_doc.client_name,
                'mobile_number':  request_doc.mobile_number,
                'gender':  request_doc.gender,
                'fitness_package':  request_doc.fitness_package,
                'no_of_sessions':  request_doc.number_of_sessions,
                'price':  request_doc.price,
                'start_day':  request_doc.start_date,
                'payment_status':  request_doc.payment_status,
                'scheduled_date_time': dates
            })

    return requests

@frappe.whitelist()
def trainer_schedule(from_date,to_date):
    doc= frappe.get_all('Service Staff',filters={'email':frappe.session.user})
    count_pt=0
    count_gx=0
    if doc:
        for d in doc:
            if type(from_date) == str:
                start = datetime.strptime(from_date, "%Y-%m-%d")
                startdate = start.date()
            else:
                startdate = from_date
            if type(to_date) == str:
                end = datetime.strptime(to_date, "%Y-%m-%d")
                enddate = end.date()
            else:
                enddate = to_date

            schedules = frappe.get_all('Fitness Training Appointment', filters={'service_staff':d.name, 'appointment_status':['not in',{'Cancelled'}], 'appointment_date':['between', [startdate, enddate]]}, order_by='appointment_date asc')
            if schedules:
                count_pt= len(schedules)
                schedule_list = []
                for schedule in schedules:
                    fitness_app = frappe.get_doc('Fitness Training Appointment', schedule.name)
                    if fitness_app.session_name:
                        session = frappe.get_doc('Client Sessions', fitness_app.session_name)

                        if fitness_app.appointment_status == "Checked-in":
                            if fitness_app.checkin_document:
                                doc = frappe.get_doc('Check In', fitness_app.checkin_document)
                                if doc.check_in_time:
                                    check_in_time = doc.check_in_time
                                    if type(check_in_time) == str:
                                        start = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                                    else:
                                        start = check_in_time
                                    check_in = datetime.strftime(start, "%H:%M")
                                else:
                                    check_in = None
                            else:
                                    check_in = None

                            schedule_list.append({
                                'appointment_id': fitness_app.name,
                                'appointment_date': fitness_app.appointment_date,
                                'appointment_time': fitness_app.appointment_time,
                                'appointment_end_time': fitness_app.appointment_end_time,
                                'appointment_status': fitness_app.appointment_status,
                                'appointment_type': fitness_app.fitness_service,
                                'client_id': fitness_app.client_id,
                                'client_name': fitness_app.client_name,
                                'member_id': fitness_app.member_id,
                                'mobile_number': fitness_app.mobile_number,
                                'fitness_trainer': fitness_app.service_staff,
                                'package_name': session.package_name,
                                'used': session.used_sessions,
                                'remaining': session.remaining_sessions,
                                'booked': session.booked_sessions,
                                'checkin_time': check_in,
                                'is_groupclass' : 0
                            })
                    
                        elif fitness_app.appointment_status == "Completed":
                            if fitness_app.checkin_document:
                                doc = frappe.get_doc('Check In', fitness_app.checkin_document)
                                
                                if doc.check_in_time:
                                    check_in_time = doc.check_in_time
                                    if type(check_in_time) == str:
                                        start = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
                                    else:
                                        start = check_in_time
                                    check_in = datetime.strftime(start, "%H:%M")
                                else:
                                    check_in = None

                                if doc.check_out_time:
                                    check_out_time = doc.check_out_time
                                    if type(check_out_time) == str:
                                        end = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M:%S")
                                    else:
                                        end = check_out_time
                                    check_out = datetime.strftime(end, "%H:%M")
                                else:
                                    check_out = None
                            else:
                                check_in = None
                                check_out = None

                            schedule_list.append({
                                'appointment_id': fitness_app.name,
                                'appointment_date': fitness_app.appointment_date,
                                'appointment_time': fitness_app.appointment_time,
                                'appointment_end_time': fitness_app.appointment_end_time,
                                'appointment_status': fitness_app.appointment_status,
                                'appointment_type': fitness_app.fitness_service,
                                'client_id': fitness_app.client_id,
                                'client_name': fitness_app.client_name,
                                'member_id': fitness_app.member_id,
                                'mobile_number': fitness_app.mobile_number,
                                'fitness_trainer': fitness_app.service_staff,
                                'package_name': session.package_name,
                                'used': session.used_sessions,
                                'remaining': session.remaining_sessions,
                                'booked': session.booked_sessions,
                                'checkin_time': check_in,
                                'checkout_time': check_out,
                                'is_groupclass' : 0
                            })
                    
                        else:                
                            schedule_list.append({
                                'appointment_id': fitness_app.name,
                                'appointment_date': fitness_app.appointment_date,
                                'appointment_time': fitness_app.appointment_time,
                                'appointment_end_time': fitness_app.appointment_end_time,
                                'appointment_status': fitness_app.appointment_status,
                                'appointment_type': fitness_app.fitness_service,
                                'client_id': fitness_app.client_id,
                                'client_name': fitness_app.client_name,
                                'member_id': fitness_app.member_id,
                                'mobile_number': fitness_app.mobile_number,
                                'fitness_trainer': fitness_app.service_staff,
                                'package_name': session.package_name,
                                'used': session.used_sessions,
                                'remaining': session.remaining_sessions,
                                'booked': session.booked_sessions,
                                'is_groupclass' : 0
                            })

            gc_list = frappe.get_all('Group Class', filters={'trainer_name':d.name, 'class_status':['not in',{'Cancelled'}], 'class_date':['between', [startdate, enddate]]}, order_by='class_date asc')
            if gc_list:
                count_gx = len(gc_list)
                for gc in gc_list:
                    group_class = frappe.get_doc('Group Class', gc.name)
                    start_time = group_class.from_time
                    if type(start_time) == str:
                        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    else:
                        start_dt = start_time
                    start = datetime.strftime(start_dt, "%H:%M:%S")

                    end_time = group_class.to_time
                    if type(end_time) == str:
                        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                    else:
                        end_dt = end_time
                    end = datetime.strftime(end_dt, "%H:%M:%S")

                    schedule_list.append({
                            'appointment_id': group_class.name,
                            'appointment_date': group_class.class_date,
                            'appointment_time': start,
                            'appointment_end_time': end,
                            'appointment_status': group_class.class_status,
                            'gc_name': group_class.group_class_name,
                            'gc_type': group_class.group_class_category,
                            'capacity': group_class.capacity,
                            'booked': group_class.booked,
                            'waitlist': group_class.in_waitlist,
                            'is_groupclass' : 1
                        })

            if schedules or gc_list:
                frappe.response["message"] = {
                    "status": 1,
                    "count": count_pt+count_gx,
                    "schedule": schedule_list
                }
            else:
                frappe.response["message"] = {
                    "status": 0,
                    "message": "No scheduled appointments"
                }
    else:
        frappe.response["message"] = {
            "status": 2,
            "message": "Trainer not found"
        }

@frappe.whitelist()
def fitness_checkin(client_id, appointment_id):
    user = frappe.get_doc('User', frappe.session.user)
    doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id,
		'check_in_type' : 'Fitness',
		'naming_series' : 'CHK-.YYYY.-FITNESS.-',
		'fitness_booking': appointment_id,
		'checked_in_by': user.full_name
        })
    doc.insert()
    doc.submit()

    frappe.db.set_value("Fitness Training Appointment", appointment_id, "appointment_status", "Checked-in")
    frappe.db.set_value("Fitness Training Appointment", appointment_id, "checkin_document", doc.name)
    frappe.db.commit()

    fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
    session = frappe.get_doc('Client Sessions', fitness_app.session_name)

    if doc.check_in_time:
        check_in_time = doc.check_in_time
        if type(check_in_time) == str:
            start = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
        else:
            start = check_in_time
        check_in = datetime.strftime(start, "%H:%M")
    else:
        check_in = None
    
    frappe.response["message"] = {
        "status": 1,
        "appointment_details": ({
            'appointment_id': fitness_app.name,
            'appointment_date': fitness_app.appointment_date,
            'appointment_time': fitness_app.appointment_time,
            'appointment_end_time': fitness_app.appointment_end_time,
            'appointment_status': fitness_app.appointment_status,
            'appointment_type': fitness_app.fitness_service,
            'client_id': fitness_app.client_id,
            'client_name': fitness_app.client_name,
            'member_id': fitness_app.member_id,
            'mobile_number': fitness_app.mobile_number,
            'fitness_trainer': fitness_app.service_staff,
            'package_name': session.package_name,
            'used': session.used_sessions,
            'remaining': session.remaining_sessions,
            'booked': session.booked_sessions,
            'checkin_time': check_in
        })
    }

@frappe.whitelist()
def complete(appointment_id):
    frappe.db.set_value("Fitness Training Appointment",appointment_id,"appointment_status","Completed")
    frappe.db.set_value("Fitness Training Appointment",appointment_id,"docstatus",1)
    frappe.db.commit()
    
    fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
    if fitness_app.checkin_document:
        doc = frappe.get_doc('Check In', fitness_app.checkin_document)
        doc.check_out_time = now_datetime()
        doc.save()
    
    if fitness_app.session==1:
        session = frappe.get_doc('Client Sessions', fitness_app.session_name)
        session.used_sessions += 1
        session.booked_sessions -= 1
        session.save()

    fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
    session = frappe.get_doc('Client Sessions', fitness_app.session_name)

    if fitness_app.checkin_document:
        if doc.check_in_time:
            check_in_time = doc.check_in_time
            if type(check_in_time) == str:
                start = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:%S")
            else:
                start = check_in_time
            check_in = datetime.strftime(start, "%H:%M")
        else:
            check_in = None
    
        if doc.check_out_time:
            check_out_time = doc.check_out_time
            if type(check_out_time) == str:
                end = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M:%S")
            else:
                end = check_out_time
            check_out = datetime.strftime(end, "%H:%M")
        else:
            check_out = None
    else:
        check_in = None
        check_out = None
    
    frappe.response["message"] = {
        "status": 1,
        "appointment_details": ({
            'appointment_id': fitness_app.name,
            'appointment_date': fitness_app.appointment_date,
            'appointment_time': fitness_app.appointment_time,
            'appointment_end_time': fitness_app.appointment_end_time,
            'appointment_status': fitness_app.appointment_status,
            'appointment_type': fitness_app.fitness_service,
            'client_id': fitness_app.client_id,
            'client_name': fitness_app.client_name,
            'member_id': fitness_app.member_id,
            'mobile_number': fitness_app.mobile_number,
            'fitness_trainer': fitness_app.service_staff,
            'package_name': session.package_name,
            'used': session.used_sessions,
            'remaining': session.remaining_sessions,
            'booked': session.booked_sessions,
            'checkin_time': check_in,
            'checkout_time': check_out
        })
    }

@frappe.whitelist()
def cancel(appointment_id):
    frappe.db.set_value("Fitness Training Appointment",appointment_id,"appointment_status","Cancelled")
    frappe.db.set_value("Fitness Training Appointment",appointment_id,"docstatus",2)
    frappe.db.commit()

    fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
    if fitness_app.session==1:
        session = frappe.get_doc('Client Sessions', fitness_app.session_name)
        session.booked_sessions -= 1
        session.save()
    
        fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
        session = frappe.get_doc('Client Sessions', fitness_app.session_name)

        frappe.response["message"] = {
            "status": 1,
            "appointment_details": ({
                'appointment_id': fitness_app.name,
                'appointment_date': fitness_app.appointment_date,
                'appointment_time': fitness_app.appointment_time,
                'appointment_end_time': fitness_app.appointment_end_time,
                'appointment_status': fitness_app.appointment_status,
                'appointment_type': fitness_app.fitness_service,
                'client_id': fitness_app.client_id,
                'client_name': fitness_app.client_name,
                'member_id': fitness_app.member_id,
                'mobile_number': fitness_app.mobile_number,
                'fitness_trainer': fitness_app.service_staff,
                'package_name': session.package_name,
                'used': session.used_sessions,
                'remaining': session.remaining_sessions,
                'booked': session.booked_sessions
            })
        }

@frappe.whitelist()
def no_show(appointment_id):
    frappe.db.set_value("Fitness Training Appointment",appointment_id,"appointment_status","No Show")
    frappe.db.set_value("Fitness Training Appointment",appointment_id,"docstatus",2)
    frappe.db.commit()
    
    appointment = frappe.get_doc('Fitness Training Appointment', appointment_id)
    
    if appointment.session==1:
        doc = frappe.get_doc('Client Sessions', appointment.session_name)
        doc.used_sessions += 1
        doc.booked_sessions -= 1
        doc.save()
    
    fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
    session = frappe.get_doc('Client Sessions', fitness_app.session_name)
    
    frappe.response["message"] = {
        "status": 1,
        "appointment_details": ({
            'appointment_id': fitness_app.name,
            'appointment_date': fitness_app.appointment_date,
            'appointment_time': fitness_app.appointment_time,
            'appointment_end_time': fitness_app.appointment_end_time,
            'appointment_status': fitness_app.appointment_status,
            'appointment_type': fitness_app.fitness_service,
            'client_id': fitness_app.client_id,
            'client_name': fitness_app.client_name,
            'member_id': fitness_app.member_id,
            'mobile_number': fitness_app.mobile_number,
            'fitness_trainer': fitness_app.service_staff,
            'package_name': session.package_name,
            'used': session.used_sessions,
            'remaining': session.remaining_sessions,
            'booked': session.booked_sessions
        })
    }

@frappe.whitelist()
def appointment_reschedule(appointment_id, date, time):
    appointment = frappe.get_doc('Fitness Training Appointment', appointment_id)
    start_time = datetime.combine(getdate(date), get_time(time))

    appointment.start_time = start_time
    appointment.save()

    fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
    session = frappe.get_doc('Client Sessions', fitness_app.session_name)

    frappe.response["message"] = {
        "status": 1,
        "appointment_details": ({
            'appointment_id': fitness_app.name,
            'appointment_date': fitness_app.appointment_date,
            'appointment_time': fitness_app.appointment_time,
            'appointment_end_time': fitness_app.appointment_end_time,
            'appointment_status': fitness_app.appointment_status,
            'appointment_type': fitness_app.fitness_service,
            'client_id': fitness_app.client_id,
            'client_name': fitness_app.client_name,
            'member_id': fitness_app.member_id,
            'mobile_number': fitness_app.mobile_number,
            'fitness_trainer': fitness_app.service_staff,
            'package_name': session.package_name,
            'used': session.used_sessions,
            'remaining': session.remaining_sessions,
            'booked': session.booked_sessions
        })
    }

@frappe.whitelist()
def new_appointment(client_id, package_name, date, time):
    start_time = datetime.combine(getdate(date), get_time(time))
    trainer = frappe.db.get("Service Staff", {"email": frappe.session.user})
    
    doc = frappe.get_doc({
		"doctype": 'Fitness Training Appointment',
		"session":1,
		"client_id": client_id,
		"session_name": package_name,
		"service_staff": trainer.name,
		"start_time" : start_time
        })
    doc.save()

    session = frappe.get_doc('Client Sessions', doc.session_name)

    frappe.response["message"] = {
        "status": 1,
        "appointment_details": ({
            'appointment_id': doc.name,
            'appointment_date': doc.appointment_date,
            'appointment_time': doc.appointment_time,
            'appointment_end_time': doc.appointment_end_time,
            'appointment_status': doc.appointment_status,
            'appointment_type': doc.fitness_service,
            'client_id': doc.client_id,
            'client_name': doc.client_name,
            'member_id': doc.member_id,
            'mobile_number': doc.mobile_number,
            'fitness_trainer': doc.service_staff,
            'package_name': session.package_name,
            'used': session.used_sessions,
            'remaining': session.remaining_sessions,
            'booked': session.booked_sessions
        })
    }

@frappe.whitelist()
def get_client(keyword):
    clients = frappe.db.sql("""
                                SELECT client.name, client.client_name, client.mobile_no, client.member_id
                                FROM `tabClient` client
							    WHERE 
                                    (client.name LIKE %s 
                                    OR client.first_name LIKE %s 
                                    OR client.last_name LIKE %s 
                                    OR client.client_name LIKE %s 
                                    OR client.mobile_no LIKE %s 
                                    OR client.member_id LIKE %s
                                    OR client.card_no LIKE %s) AND client.membership_status = 'Member'
                            """, ("%"+keyword+"%", "%"+keyword+"%", "%"+keyword+"%", "%"+keyword+"%", "%"+keyword+"%", "%"+keyword+"%", "%"+keyword+"%"), as_dict=1)
    return clients

@frappe.whitelist()
def get_package(client_id):
    sessions = frappe.get_all('Client Sessions', filters={'client_id': client_id, 'session_status': 'Active', 'remaining_sessions': ['>', 0], 'service_type': 'Fitness Services'})
    package = []
    if sessions:
        for session_one in sessions:
            session = frappe.get_doc('Client Sessions', session_one.name)
            booked = session.remaining_sessions - session.booked_sessions
            if booked != 0:
                package.append({
                    "package_id": session.name,
                    "package_name": session.package_name,
                    "used": session.used_sessions,
                    "booked": session.booked_sessions,
                    "remaining": session.remaining_sessions
                })
    
    if package:
        frappe.response["message"] = {
            "status": 1,
            "package_details": package
        }
    else:
        frappe.response["message"] = {
            "status": 0,
            "package_details": package
        }

@frappe.whitelist()
def refresh_appointment(appointment_id):
    fitness_app = frappe.get_doc('Fitness Training Appointment', appointment_id)
    session = frappe.get_doc('Client Sessions', fitness_app.session_name)

    frappe.response["message"] = {
        "status": 1,
        "appointment_details": ({
            'appointment_id': fitness_app.name,
            'appointment_date': fitness_app.appointment_date,
            'appointment_time': fitness_app.appointment_time,
            'appointment_end_time': fitness_app.appointment_end_time,
            'appointment_status': fitness_app.appointment_status,
            'appointment_type': fitness_app.fitness_service,
            'client_id': fitness_app.client_id,
            'client_name': fitness_app.client_name,
            'member_id': fitness_app.member_id,
            'mobile_number': fitness_app.mobile_number,
            'fitness_trainer': fitness_app.service_staff,
            'package_name': session.package_name,
            'used': session.used_sessions,
            'remaining': session.remaining_sessions,
            'booked': session.booked_sessions
        })
    }

@frappe.whitelist()
def view_gc_attendees(appointment_id):
    attendee_list=[]
    gc_attendees = frappe.get_all('Group Class Attendees', filters={'group_class': appointment_id, 'attendee_status':['not in',{'Cancelled'}]}, fields={'client_id', 'client_name', 'mobile_number'})
    if gc_attendees:
        for gc in gc_attendees:
            attendee_list.append({
                "client_id": gc.client_id,
                "client_name": gc.client_name,
                "mobile_no": gc.mobile_number
            })
    
    frappe.response["message"] = {
            "status": 1,
            "attendee_details": attendee_list
    }

@frappe.whitelist()
def complete_gc(appointment_id):
    frappe.db.set_value('Group Class', appointment_id, {
        'class_status': "Completed",
        'docstatus': 1
    })
    frappe.db.commit()

    gc_attendees =  frappe.get_all('Group Class Attendees', filters={'group_class': appointment_id, 'attendee_status': 'Checked-in'})
    if gc_attendees:
        for attendee in gc_attendees:
            frappe.db.set_value('Group Class Attendees', attendee.name, {
                'attendee_status': "Complete",
                'docstatus': 1
            })
            frappe.db.commit()
    
    frappe.response["message"] = {
        "status": 1,
        "message": "Group Class Completed"
    }

@frappe.whitelist()
def cancel_gc(appointment_id):
    frappe.db.set_value('Group Class', appointment_id, {
        'class_status': "Cancelled",
        'docstatus': 2
    })
    frappe.db.commit()

    gc_attendees =  frappe.get_all('Group Class Attendees', filters={'group_class': appointment_id})
    if gc_attendees:
        for attendee in gc_attendees:
            frappe.db.set_value('Group Class Attendees', attendee.name, {
                'attendee_status': "Cancelled",
                'docstatus': 2
            })
            frappe.db.commit()

    frappe.response["message"] = {
        "status": 1,
        "message": "Group Class Cancelled"
    }

@frappe.whitelist()
def gc_checkin(attendee_list):
    user = frappe.get_doc('User',frappe.session.user)
    for attendees in attendee_list:
        attendee =  frappe.get_doc('Group Class Attendees', attendees.name)
        doc = frappe.get_doc({
            'doctype': 'Check In',
            'client_id': attendee.client_id,
            'check_in_type' : 'Group Class',
            'naming_series' : 'CHK-.YYYY.-GC.-',
            'class_attendee_id': attendee.name,
            'checked_in_by': user.full_name
        })
        doc.submit()
        frappe.db.set_value("Group Class Attendees", attendee.name, "attendee_status", "Checked-in")
        frappe.db.set_value("Group Class Attendees", attendee.name, "checkin_document", doc.name)
