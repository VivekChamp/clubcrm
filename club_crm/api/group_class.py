import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_group_class():
    group_class = frappe.get_all('Group Class', filters={'on_app':1,'docstatus':1,'status':"Open"}, fields=['name','date','group_class_name','class_type','class_category','trainer_name','capacity','remaining','from_time','to_time','members_only'])
    frappe.response["message"] = {
        "Group Class": group_class
         }

@frappe.whitelist()
def create_attendee(client_id,class_id):
    check= frappe.get_all('Group Class Attendees', filters={'group_class':class_id, 'client_id':client_id})
    
    if check:
        frappe.response["message"] = {
        "Status": 0,
        "Status Message":"This client has already enrolled for this class"
        }
    
    else:
        doc= frappe.get_doc({
            'doctype': 'Group Class Attendees',
            'group_class':class_id,
            'client_id': client_id
            })
        doc.insert()
        doc.submit()
        frappe.response["message"] = {
        "Status": 1,
        "Status Message":"Enrollment successful"
        }
