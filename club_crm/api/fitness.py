import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _
from club_crm.api.wallet import get_balance

@frappe.whitelist()
def get_fitness_category(client_id):
    doc= frappe.get_list('Fitness Training Request', filters={'client_id':client_id, 'request_status':['in', {'Pending','Scheduled'}], 'docstatus':1}, fields=['*'])
    if doc:
        doc_1=doc[0]
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
                "Status Message": "Training has been scheduled",
                "Document ID": doc_1.name,
                "rate": doc_1.price,
                "package_name": doc_1.fitness_package,
                "Number of Sessions": doc_1.number_of_sessions,
                "Schedule": schedule
                }
    else:
        fitness_category = frappe.get_all('Fitness Training Category', filters={'on_app': 1}, fields=['category_name','category_image'])
        frappe.response["message"] = {
            "Status":2,
            "Fitness Categories": fitness_category
            }

@frappe.whitelist()
def get_fitness_package(fitness_category):
    fitness_package = frappe.get_all('Fitness Training Package', filters={'on_app': 1, 'fitness_category':fitness_category}, fields=['name','duration','no_of_session','validity','sessions_per_week','price','fitness_category'])
    frappe.response["message"] = {
        "Fitness Categories": fitness_package
         }

@frappe.whitelist()
def get_trainer(fitness_package,client_id):
    client= frappe.get_doc('Client', client_id)
    #spa_group= frappe.get_doc('Spa Menu Group', doc.spa_menu_group)
    fit_trainer= frappe.get_all('Fitness Package Assignment', filters={'fitness_package':fitness_package, 'on_app':1}, fields=['name','parent','parenttype','parentfield'])
    trainer=[]
    for name in fit_trainer:
        doc_1= frappe.get_doc('Fitness Trainer', name.parent)
        if doc_1.on_app==1:
            if client.membership_status=="Non-Member":
                if doc_1.gender==client.gender:
                    trainer.append({
                        'Trainer': doc_1.employee_name,
                        'Description': doc_1.description,
                        'Image': doc_1.image,
                        'Gender': doc_1.gender
                        })
            else:
                trainer.append({
                    'Trainer': doc_1.employee_name,
                    'Description': doc_1.description,
                    'Image': doc_1.image,
                    'Gender': doc_1.gender
                    })
    return trainer

@frappe.whitelist()
def get_appointments(client_id):
    doc = frappe.get_list('Fitness Training Appointment', filters={'client_id':client_id, 'docstatus':1}, fields=['name','date','client_id','client_name','package_name','trainer_name','status','start_time','end_time','payment_status'])
    details=[]
    if doc:
        for rating in doc:
            rate=frappe.get_list('Rating', filters={'document_id':rating.name}, fields=['rating_point'])
            if rate:
                rate=rate[0]
                details.append({
                    'pt_appointment': rating,
                    'Rating': rate.rating_point
                    })
            else:
                details.append({
                    'pt_appointment':rating,
                    'Rating': -1
                    })
        return details

@frappe.whitelist()
def cancel_request(doc_id):
    doc= frappe.get_doc('Fitness Training Request', doc_id)
    if doc.docstatus==1:
        frappe.db.set_value('Fitness Training Request', doc_id, {
            'request_status': 'Cancelled',
            'docstatus': 2
            })
        doc.reload()
        frappe.response["message"] = {
        "status": 1,
        "status_message": "Fitness Training Request has been cancelled"
         }
    else:
        frappe.response["message"] = {
            "status": 0,
            "status_message": "Fitness Training Appointmnent already cancelled"
            }


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
            "status_message": "Fitness Training Appointmnent already cancelled"
            }

@frappe.whitelist()
def proceed_payment(client_id,doc_id, payment_method):
    doc= frappe.get_doc('Fitness Training Request', doc_id)
    doc.payment_method= payment_method
    doc.save()
    wallet= get_balance(client_id)
    frappe.response["message"] = {
        "status": 1,
        "document_name": doc.name,
        "wallet_balance": wallet
        }