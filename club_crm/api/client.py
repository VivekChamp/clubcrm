import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_client(mobile_no):
    client = frappe.get_all('Client', filters={'mobile_no': mobile_no}, fields=['name','first_name','last_name','client_name','gender','birth_date','nationality','qatar_id','email','mobile_no','membership_status','image','apply_membership','mem_application','status','customer_group','territory','marital_status','allergies','medication','medical_history','other_notes'])
    frappe.response["message"] =  {
		"client_details": client
                }

@frappe.whitelist()
def medical_history(client_id,allergies,medication,history,notes):
    client= frappe.get_doc('Client', client_id)
    client.allergies=allergies
    client.medication=medication
    client.medical_history=history
    client.other_notes=notes
    client.save()
    frappe.response["message"] =  {
		"Status": 1
    }

@frappe.whitelist()
def get_medical_history(client_id):
    doc= frappe.get_doc('Client', client_id)
    frappe.response["message"] = {
        "medical_history": doc.medical_history,
        "allergies": doc.allergies,
        "medication": doc.medication,
        "other_notes": doc.other_notes
    }