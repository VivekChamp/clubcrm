import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe.utils import getdate, get_time, flt, now_datetime
from datetime import datetime, timedelta, date, time
from frappe import throw, msgprint, _
from club_crm.api.wallet import get_balance

@frappe.whitelist()
def get_fitness_category(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    if not client.status == "Disabled":
        doc = frappe.get_all('Fitness Training Request', filters={'client_id':client.name, 'request_status':['in', {'Pending','Scheduled'}]}, fields=['*'])
        if doc:
            for doc_1 in doc:
                if doc_1.request_status=="Pending":
                    frappe.response["message"] = {
                    "Status":0,
                    "Status Message": "A pending request exists",
                    "Document ID" : doc_1.name
                    }
                else:
                    schedule=frappe.get_list('Fitness Training Trainer Scheduler', filters={'parent':doc_1.name,'parentfield':'table_schedule'}, fields=['day','date','from_time','to_time'], order_by="date asc")
                    
                    frappe.response["message"] = {
                        "Status":1,
                        "disabled": 0,
                        "Status Message": "Training has been scheduled",
                        "Document ID": doc_1.name,
                        "rate": doc_1.price,
                        "package_name": doc_1.fitness_package,
                        "Number of Sessions": doc_1.number_of_sessions,
                        "Schedule": schedule
                        }
        else:
            fitness_category = frappe.get_all('Fitness Services', filters={'on_app': 1}, fields=['fitness_name','image'])
            fitness_item = []
            for item in fitness_category:
                fitness_item.append({
                    "category_name" : item.fitness_name,
                    "category_image" : item.image
                })
            frappe.response["message"] = {
                "Status":2,
                "disabled": 0,
                "Fitness Categories": fitness_item
            }
    else:
        frappe.response["message"] = {
                "Status":3,
                "disabled": 1
        }

@frappe.whitelist()
def get_fitness_package(fitness_category):
    fit_category = frappe.get_doc('Fitness Services', fitness_category)
    all_fitness_package = frappe.get_all('Club Packages', filters={'on_app': 1, 'package_type': 'Fitness'})
    packages = []
    for item in all_fitness_package:
        single_package = frappe.get_doc('Club Packages', item.name)
        for package in single_package.package_table:
            if package.service_name == fitness_category:
                sessions = int(package.no_of_sessions/4)
                if sessions == 0:
                    sessions = 1
                validity = int(package.validity // (24 * 3600))
                packages.append({
                    "name": item.name,
                    "duration": int(fit_category.duration),
                    "no_of_session": package.no_of_sessions,
                    "validity": validity,
                    "sessions_per_week": sessions,
                    "price": package.price,
                    "fitness_category": fitness_category
                })
    
    frappe.response["message"] = {
        "Fitness Categories": packages
    }

@frappe.whitelist()
def get_trainer(fitness_package,client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    club_package = frappe.get_doc('Club Packages', fitness_package)
    for package in club_package.package_table:
        fit_trainer = frappe.get_all('Fitness Services Assignment', filters={'fitness_package': package.service_name, 'on_app':1}, fields=['name','parent','parenttype','parentfield','gender_preference'])
        trainers = []
        for trainer in fit_trainer:
            doc_1 = frappe.get_doc('Service Staff', trainer.parent)
            if doc_1.on_app == 1:
                if trainer.gender_preference == "Same Gender":
                    if doc_1.gender == client.gender:
                        trainers.append({
                            'Trainer': doc_1.display_name,
                            'Description': doc_1.description,
                            'Image': doc_1.image,
                            'Gender': doc_1.gender
                        })
                elif trainer.gender_preference == "No Preference":
                    trainers.append({
                            "Trainer": doc_1.display_name,
                            "Description": doc_1.description,
                            "Image": doc_1.image,
                            "Gender": doc_1.gender
                        })
        return trainers

@frappe.whitelist()
def get_pt_appointments():
    rating_point = -1
    disabled = 0
    client = frappe.db.get("Client", {"email": frappe.session.user})
    if client.status == "Disabled":
        disabled = 1
    time = frappe.get_doc('Fitness Training Settings')

    sessions = []
    client_session_list = frappe.get_all('Client Sessions', filters={'client_id': client.name, 'session_status': 'Active', 'package_type': 'Fitness'}, order_by="expiry_date asc")
    if client_session_list:
        for client_session in client_session_list:
            client_session_doc = frappe.get_doc('Client Sessions', client_session.name)
            sessions.append({
                'package_name': client_session_doc.package_name,
                'expiry_date' : client_session_doc.expiry_date,
                'used_sessions': client_session_doc.used_sessions,
                'remaining_sessions': client_session_doc.remaining_sessions
            })

    details=[]
    pt_list = frappe.get_all('Fitness Training Appointment', filters={'client_id':client.name}, fields=['name','start_time'], order_by="appointment_date asc")
    if pt_list:
        for pt in pt_list:
            pt_doc = frappe.get_doc('Fitness Training Appointment', pt.name)
            cancel_time = pt_doc.start_time - timedelta(seconds=int(time.pt_cancellation_time))
            start_date = pt_doc.start_time.date()

            rating_list = frappe.get_all('Rating', filters={'document_id':pt.name}, fields=['rating_point'])
            if rating_list:
                for rating in rating_list:
                    rating_point = rating.rating_point
            details.append({
                "name": pt_doc.name,
                "date": start_date,
                "client_id" : pt_doc.client_id,
                "client_name": pt_doc.client_name,
                "package_name": pt_doc.fitness_service,
                "trainer_name": pt_doc.service_staff,
                "status": pt_doc.appointment_status,
                "start_time": pt_doc.start_time,
                "end_time": pt_doc.end_time,
                "payment_status": pt_doc.payment_status,
                "cancellation_time" : cancel_time,
                "rating": rating_point
            })

    frappe.response["message"] = {
        "disabled": disabled,
        "pt_appointments": details,
        "packages": sessions
    }

@frappe.whitelist()
def get_appointments(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_all('Fitness Training Appointment', filters={'client_id':client.name}, fields=['name','booking_date','client_id','client_name','fitness_service','service_staff','appointment_status','start_time','end_time','payment_status'], order_by="appointment_date asc")
    details=[]
    if doc:
        for rating in doc:
            # start_time = datetime.strftime(rating.start_time, "%H:%M:%S")
            # end_time = datetime.strftime(rating.end_time, "%H:%M:%S")
            start_date = rating.start_time.date()

            rate=frappe.get_all('Rating', filters={'document_id':rating.name}, fields=['rating_point'])
            #cancel_time = rating.start_time - timedelta(seconds=int(time.spa_cancel_time))
            if rate:
                rate=rate[0]
                details.append({
                    'pt_appointment': {
                        "name": rating.name,
                        "date": start_date,
                        "client_id" : rating.client_id,
                        "client_name": rating.client_name,
                        "package_name": rating.fitness_service,
                        "trainer_name": rating.service_staff,
                        "status": rating.appointment_status,
                        "start_time": rating.start_time,
                        "end_time": rating.end_time,
                        "payment_status": rating.payment_status
                    },
                    'Rating': rate.rating_point,
                })
            else:
                details.append({
                    'pt_appointment': {
                        "name": rating.name,
                        "date": start_date,
                        "client_id" : rating.client_id,
                        "client_name": rating.client_name,
                        "package_name": rating.fitness_service,
                        "trainer_name": rating.service_staff,
                        "status": rating.appointment_status,
                        "start_time": rating.start_time,
                        "end_time": rating.end_time,
                        "payment_status": rating.payment_status
                    },
                    'Rating': -1,
                })
        return details

@frappe.whitelist()
def cancel_request(doc_id):
    doc = frappe.get_doc('Fitness Training Request', doc_id)
    frappe.db.set_value('Fitness Training Request', doc_id, {
        'request_status': 'Cancelled',
        'docstatus': 2
    })
    doc.reload()
    frappe.response["message"] = {
        "status": 1,
        "status_message": "Fitness Training Request has been cancelled"
    }
    # else:
    #     frappe.response["message"] = {
    #         "status": 0,
    #         "status_message": "Fitness Training Appointmnent already cancelled"
    #         }


@frappe.whitelist()
def cancel_session(appointment_id):
    doc= frappe.get_doc('Fitness Training Appointment', appointment_id)
    if doc.docstatus==1:
        frappe.db.set_value('Fitness Training Appointment', appointment_id, {
            'status': 'Cancelled',
            'docstatus': 2
            })
        doc.reload()
        frappe.response["message"] = {
            "status": 1,
            "status_message": "Fitness Training Appointment has been cancelled"
        }
    else:
        frappe.response["message"] = {
            "status": 0,
            "status_message": "Fitness Training Appointment already cancelled"
        }

@frappe.whitelist()
def proceed_payment(client_id,doc_id, payment_method):
    doc = frappe.get_doc('Fitness Training Request', doc_id)
    # doc.payment_method= payment_method
    # doc.save()
    # cart = add_cart_from_pt_online(doc.client_id, doc.name)
    wallet= get_balance()
    frappe.response["message"] = {
        "status": 1,
        "document_name": doc.name,
        "wallet_balance": wallet
        }

@frappe.whitelist(allow_guest=True)
def update_mem(doc_id):
    doc = frappe.get_doc("Memberships Application", doc_id)
    doc.append('membership_payment', {
        "mode_of_payment": "Online Payment",
        "paid_amount": doc.grand_total
		})
    doc.save(ignore_permissions=True)