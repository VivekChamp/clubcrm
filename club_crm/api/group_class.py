import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from datetime import datetime
from frappe.utils import getdate, get_time, flt
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_group_class():
    client = frappe.db.get("Client", {"email": frappe.session.user})
    group_class = frappe.get_all('Group Class', filters={'on_app':1, 'enabled':1, 'booking_status': 'Available', 'class_status': ['not in', {'Cancelled'}]}, fields=['name','group_class_name','group_class_image','group_class_type','group_class_category','trainer_name','capacity','remaining','class_date','class_from_time','for_gender','class_to_time','members_only'], order_by="class_date asc")
    group_class_list = []
    if group_class:
        for gc_class in group_class:
            if gc_class.for_gender == client.gender or gc_class.for_gender == "Mixed" or not gc_class.for_gender:
                gc_service = frappe.get_doc('Group Class Services', gc_class.group_class_name)
                start_time = convert24(gc_class.class_from_time)
                end_time = convert24(gc_class.class_to_time)
                start_dt = "%s %s" % (gc_class.class_date, start_time or "00:00:00")
                end_dt = "%s %s" % (gc_class.class_date, end_time or "00:00:00")
                group_class_list.append({
                    "name": gc_class.name,
                    "date": start_dt,
                    "group_class_name": gc_class.group_class_name,
                    "image": gc_service.group_class_image,
                    "class_type": gc_class.group_class_type,
                    "class_category": gc_class.group_class_category,
                    "trainer_name": gc_class.trainer_name,
                    "capacity": str(gc_class.capacity),
                    "remaining": str(gc_class.remaining),
                    "from_time": start_dt,
                    "to_time": end_dt,
                    "members_only": gc_class.members_only
                })

    frappe.response["message"] = {
        "Group Class": group_class_list
    }

@frappe.whitelist()
def create_attendee(client_id, class_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    check = frappe.get_all('Group Class Attendees', filters={'group_class':class_id, 'client_id':client.name, 'attendee_status': ['not in',{'Waiting List', 'Cancelled', 'No Show'}]})
    
    if check:
        frappe.response["message"] = {
        "Status": 0,
        "Status Message":"This client has already enrolled for this class"
        }
    
    else:
        doc = frappe.get_doc({
            'doctype': 'Group Class Attendees',
            'group_class': class_id,
            'client_id': client.name
            })
        doc.save()

        frappe.response["message"] = {
        "Status": 1,
        "Status Message":"Enrollment successful"
        }

@frappe.whitelist()
def get_details(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_all('Group Class Attendees', filters={'client_id':client.name, 'attendee_status':['not in', {'Cancelled', 'Waiting List'}]}, fields=['name','group_class','group_class_name','trainer_name','class_status','class_date','from_time','to_time'], order_by="class_date asc")
    details=[]
    if doc:
        for rating in doc:
            start_time = convert24(rating.from_time)
            end_time = convert24(rating.to_time)
            start_time_dt = "%s %s" % (rating.class_date, start_time or "00:00:00")
            end_time_dt = "%s %s" % (rating.class_date, end_time or "00:00:00")
            rate = frappe.get_all('Rating', filters={'document_id':rating.group_class}, fields=['rating_point'])

            if rate:
                rate=rate[0]
                details.append({
                    'Group Class': {
                        "name": rating.name,
                        "group_class": rating.group_class,
                        "group_class_name": rating.group_class_name,
                        "trainer_name": rating.trainer_name,
                        "class_status": rating.class_status,
                        "from_time": start_time_dt,
                        "to_time": end_time_dt
                    },
                    'Rating': rate.rating_point
                })
            else:
                details.append({
                    'Group Class': {
                        "name": rating.name,
                        "group_class": rating.group_class,
                        "group_class_name": rating.group_class_name,
                        "trainer_name": rating.trainer_name,
                        "class_status": rating.class_status,
                        "from_time": start_time_dt,
                        "to_time": end_time_dt
                    },
                    'Rating': -1
                })
        return details

@frappe.whitelist()
def cancel_attendee(group_class_attendee_id):
    frappe.db.set_value('Group Class Attendees', group_class_attendee_id, {
        'attendee_status': "Cancelled",
        'docstatus': 2
        })
    frappe.db.commit()

    doc = frappe.get_doc('Group Class Attendees', group_class_attendee_id )
    group_class = frappe.get_doc('Group Class', doc.group_class)
    group_class.booked -= 1
    group_class.save()

    if group_class.booking_status == "Full":
        frappe.db.set_value('Group Class', group_class.name, 'booking_status', 'Available')
        frappe.db.commit()

    frappe.response["message"] = {
        "Status": 1,
        "Status Message":"Group Class enrollment cancelled"
        }

@frappe.whitelist()
def convert24(str1):
	if str1[-3:] == " AM" and str1[:2] == "12":
		return "00" + str1[2:-3]
	elif str1[-3:] == " AM":
		return str1[:-3]
	elif str1[-3:] == " PM" and str1[:2] == "12":
		return str1[:-3]
	else:
		return str(int(str1[:2]) + 12) + str1[2:8]