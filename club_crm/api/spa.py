import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_spa_category():
    spa_category = frappe.get_all('Spa Menu Category', filters={'on_app': 1}, fields=['spa_category_name','category_image'])
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
    #spa_group= frappe.get_doc('Spa Menu Group', doc.spa_menu_group)
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
    doc = frappe.get_all('Spa Appointment', filters={'client_id':client_id, 'docstatus':1}, fields=['name','spa_item','duration','status','appointment_date','appointment_time','rate','therapist_name'])
    details=[]
    if doc:
        for rating in doc:
            rate=frappe.get_all('Rating', filters={'document_id':rating.name}, fields=['rating_point'])
            if rate:
                rate=rate[0]
                details.append({
                    'Spa Appointment': rating,
                    'Rating': rate.rating_point
                    })
            else:
                details.append({
                    'Spa Appointment':rating,
                    'Rating': -1
                    })
        return details
