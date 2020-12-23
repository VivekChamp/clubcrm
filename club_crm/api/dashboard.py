import frappe
from datetime import datetime, date
from frappe.utils import now_datetime
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_dashboard_details(client_id):
    today = date.today()
    valet= frappe.get_list('Valet Parking', filters={'client_id': client_id, 'date': today, 'status': ['in', {'Parked','Requested for Delivery','Ready for Delivery'}]}, fields=['name', 'vehicle_no','status'])
    if valet:
        val=valet[0]
        if val.status=="Requested for Delivery":
            valet_parking = "Requested"
        elif val.status=="Ready for Delivery":
            valet_parking = "Vehicle Ready"
        else:
            valet_parking= "Parked"
    else:
        valet_parking=None

    checkin= frappe.get_list('Check In', filters={'client_id': client_id, 'check_in_type': 'Member Check-in'}, fields={'name', 'check_in_time'}, order_by="check_in_time desc")
    if checkin:
        check=checkin[0]
        check_in = check.check_in_time.date()
    else:
        check_in=None

    f= frappe.get_list('Food Order Entry', filters={'client_id': client_id, 'date': today, 'order_status': ['in', {"Ordered","Ready"}]}, fields={'name', 'order_status'}, order_by="creation asc")
    if f:
        food=f[0]
        food_order=food.order_status
    else:
        food_order=None

    group_class= frappe.get_list('Group Class Attendees', filters={'client_id':client_id, 'class_status':['in', {'Open','Scheduled'}]}, fields={'group_class_name', 'from_time'}, order_by="from_time asc")
    if group_class:
        gc=group_class[0]
        grp_class = gc.from_time.date()
    else:
        grp_class=None
    
    pt= frappe.get_list('Fitness Training Appointment', filters={'client_id':client_id, 'docstatus':'1', 'status':['in', {'Open','Scheduled'}]})
    if pt:
        fitness= len(pt)
    else:
        fitness=None

    spa= frappe.get_list('Spa Appointment', filters={'client_id':client_id, 'status':['in', {'Open','Scheduled'}]}, fields={'start_time'}, order_by="start_time asc")
    if spa:
        t=spa[0]
        spa_next=t.start_time.date()
    else:
        spa_next= None
    
    frappe.response["message"] = {
        "Valet": valet_parking,
        "checkin": check_in,
        "food_order": food_order,
        "group_class": grp_class,
        "fitness": len(pt),
        "spa": spa_next
         }