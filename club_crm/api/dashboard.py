import frappe
from datetime import datetime, date
from frappe.utils import now_datetime
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_dashboard_details(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    today = date.today()
    valet = frappe.get_list('Valet Parking', filters={'client_id': client.name, 'date': today, 'status': ['in', {'Parked','Requested for Delivery','Ready for Delivery'}]}, fields=['name', 'vehicle_no','status'])
    if valet:
        val = valet[0]
        valet_name = val.name
        if val.status == "Requested for Delivery":
            valet_parking = "Requested"
        elif val.status == "Ready for Delivery":
            valet_parking = "Vehicle Ready"
        else:
            valet_parking= "Parked"
    else:
        valet_name = None
        valet_parking = None

    checkin = frappe.get_list('Check In', filters={'client_id': client.name, 'check_in_type': 'Club Check-in'}, fields={'name', 'check_in_time'}, order_by="check_in_time desc")
    if checkin:
        check = checkin[0]
        check_in = check.check_in_time.date()
    else:
        check_in = None

    f = frappe.get_list('Food Order Entry', filters={'client_id': client.name, 'date': today, 'order_status': ['in', {"Ordered","Ready"}]}, fields={'name', 'order_status'}, order_by="creation asc")
    if f:
        food = f[0]
        food_order = food.order_status
    else:
        food_order = None

    group_class = frappe.get_list('Group Class Attendees', filters={'client_id': client.name, 'attendee_status':['in', {'Open','Scheduled'}]}, fields={'group_class_name', 'class_date'}, order_by="from_time asc")
    if group_class:
        gc = group_class[0]
        grp_class = gc.class_date
    else:
        grp_class = None
    
    pt = frappe.get_list('Fitness Training Appointment', filters={'client_id': client.name, 'docstatus':'1', 'status':['in', {'Open','Scheduled'}]})
    if pt:
        fitness = len(pt)
    else:
        fitness = None

    spa = frappe.get_list('Spa Appointment', filters={'client_id': client.name, 'appointment_status':['in', {'Open','Scheduled'}]}, fields={'start_time'}, order_by="start_time asc")
    if spa:
        t = spa[0]
        spa_next = t.start_time.date()
    else:
        spa_next = None
    
    assigned_cec = None
    mobile_no = None
    if client.assigned_to:
        assigned_cec = client.assigned_to
        staff = frappe.get_doc('Service Staff', client.assigned_to)
        if staff.mobile_no:
            mobile_no = '+974 ' + str(staff.mobile_no)
    
    frappe.response["message"] = {
        "Valet": valet_parking,
        "valet_id": valet_name,
        "checkin": check_in,
        "food_order": food_order,
        "group_class": grp_class,
        "fitness": fitness,
        "spa": spa_next,
        "assigned_cec": assigned_cec,
        "cec_contact": mobile_no
    }

@frappe.whitelist()
def get_nonmember_dashboard(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    spa = frappe.get_list('Spa Appointment', filters={'client_id': client.name, 'appointment_status':['in', {'Open','Scheduled'}]}, fields={'start_time'}, order_by="start_time asc")
    if spa:
        t=spa[0]
        spa_next=t.start_time.date()
    else:
        spa_next= None
    
    club_tour = frappe.get_list('Club Tour', filters={'client_id': client.name,'tour_status':['in', {'Pending','Scheduled'}]})
    if club_tour:
        s= club_tour[0]
        club_tour= s.tour_status
    else:
        club_tour= None
    
    assigned_cec = None
    mobile_no = None
    if client.assigned_to:
        assigned_cec = client.assigned_to
        staff = frappe.get_doc('Service Staff', client.assigned_to)
        if staff.mobile_no:
            mobile_no = '+974 ' + str(staff.mobile_no)

    frappe.response["message"] = {
        "spa": spa_next,
        "club_tour": club_tour,
        "assigned_cec": assigned_cec,
        "cec_contact": mobile_no
        }

@frappe.whitelist(allow_guest=True)
def get_terms():
    terms = frappe.get_doc('App Settings')
    frappe.response["message"] = {
        "spa_terms": terms.spa_tc,
        "spa_cancellation": terms.spa_cancellation,
        "fitness_terms": terms.fitness_tc,
        "fitness_cancellation": terms.fitness_cancellation,
        "user_terms": terms.user_tc,
        "membership_terms": terms.mem_app_tc
        }