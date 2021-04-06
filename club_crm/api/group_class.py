import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from datetime import datetime
from frappe.utils import getdate, get_time, flt
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_group_class():
    group_class = frappe.get_all('Group Class', filters={'on_app':1, 'enabled':1, 'booking_status':"Available"}, fields=['name','group_class_name','group_class_image','group_class_type','group_class_category','trainer_name','capacity','remaining','class_date','class_from_time','class_to_time','members_only'])
    group_class_list = []
    if group_class:
        for gc_class in group_class:
            group_class_list.append({
                "name": gc_class.name,
                "date": gc_class.class_date,
                "group_class_name": gc_class.group_class_name,
                "image": gc_class.group_class_image,
                "class_type": gc_class.group_class_type,
                "class_category": gc_class.group_class_category,
                "trainer_name": gc_class.trainer_name,
                "capacity": gc_class.capacity,
                "remaining": gc_class.remaining,
                "from_time": gc_class.class_from_time,
                "to_time": gc_class.class_to_time,
                "members_only": gc_class.members_only
            })

    frappe.response["message"] = {
        "Group Class": group_class_list
    }

@frappe.whitelist()
def create_attendee(client_id, class_id):
    check = frappe.get_all('Group Class Attendees', filters={'group_class':class_id, 'docstatus':1, 'client_id':client_id})
    
    if check:
        frappe.response["message"] = {
        "Status": 0,
        "Status Message":"This client has already enrolled for this class"
        }
    
    else:
        doc= frappe.get_doc({
            'doctype': 'Group Class Attendees',
            'group_class': class_id,
            'client_id': client_id,
            'class_status': "Scheduled"
            })
        doc.insert()
        doc.submit()
        frappe.response["message"] = {
        "Status": 1,
        "Status Message":"Enrollment successful"
        }

@frappe.whitelist()
def get_details(client_id):
    doc = frappe.get_all('Group Class Attendees', filters={'client_id':client_id,'docstatus':1}, fields=['name','group_class','group_class_name','trainer_name','class_status','from_time','to_time'])
    details=[]
    if doc:
        for rating in doc:
            rate = frappe.get_all('Rating', filters={'document_id':rating.group_class}, fields=['rating_point'])
            if rate:
                rate=rate[0]
                details.append({
                    'Group Class': rating,
                    'Rating': rate.rating_point
                    })
            else:
                details.append({
                    'Group Class':rating,
                    'Rating': -1
                })
        return details

@frappe.whitelist()
def cancel_attendee(group_class_attendee_id):
    doc= frappe.get_doc('Group Class Attendees', group_class_attendee_id)
    doc.cancel()
    frappe.response["message"] = {
        "Status": 1,
        "Status Message":"Group Class enrollment cancelled"
        }
