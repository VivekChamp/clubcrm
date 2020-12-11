import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_fitness_category(client_id):
    doc= frappe.get_all('Fitness Training Request', filters={'client_id':client_id, 'request_status':['in', {'Pending','Scheduled'}], 'docstatus':1}, fields=['*'])
    if doc:
        doc_1=doc[0]
        if doc_1.request_status=="Pending":
            frappe.response["message"] = {
            "Status":0,
            "Status Message": "A pending request exists",
            "Document ID" : doc_1.name
            }
        else:
            schedule=frappe.get_all('Fitness Training Trainer Scheduler', filters={'parent':doc_1.name}, fields=['day','date','from_time','to_time'], order_by="date asc")
            frappe.response["message"] = {
                "Status":1,
                "Status Message": "Training has been scheduled",
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