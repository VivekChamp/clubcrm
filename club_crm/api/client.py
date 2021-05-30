import frappe
from datetime import datetime, date
from frappe.utils import now_datetime
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
    client = frappe.db.get("Client", {"email": frappe.session.user})
    frappe.db.set_value('Client', client.name, {
      'allergies': allergies,
      'medication': medication,
      'medical_history': history,
      'other_notes': notes
    })
    frappe.response["message"] = {
      "Status": 1
    }

@frappe.whitelist()
def get_medical_history(client_id):
    doc = frappe.db.get("Client", {"email": frappe.session.user})
    frappe.response["message"] = {
        "medical_history": doc.medical_history,
        "allergies": doc.allergies,
        "medication": doc.medication,
        "other_notes": doc.other_notes
    }

@frappe.whitelist()
def update_fcm_token(token):
  client = frappe.db.get("Client", {"email": frappe.session.user})
  if client:
    frappe.db.set_value("Client", client.name, "fcm_token", token)
    frappe.response["message"] = {
      "status": 1,
      "status_message": "FCM Token updated" 
    }
  else:
    frappe.response["message"] = {
      "status": 0,
      "status_message": "Client error"
    }

@frappe.whitelist()
def get_client_details():
  today = date.today()
  client_details = []
  cec_mobile_no = None
  valet_name = None
  valet_parking = None
  check_in = None
  food_order = None
  group_class = None
  fitness = None
  spa_next = None
  club_tour_status = None

  app_settings = frappe.get_doc('App Settings')
  
  client=frappe.db.get("Client", {"email": frappe.session.user})
  if client.assigned_to:
    staff = frappe.get_doc('Service Staff', client.assigned_to)
    if staff.mobile_no:
      cec_mobile_no = '+974 '+str(staff.mobile_no)
  
  if client.membership_status == "Member":
    valet_list = frappe.get_all('Valet Parking', filters={'client_id': client.name, 'date': today, 'status': ['in', {'Parked','Requested for Delivery','Ready for Delivery'}]}, fields=['name', 'vehicle_no','status'])
    if valet_list:
        valet = valet_list[0]
        valet_name = valet.name
        if valet.status == "Requested for Delivery":
            valet_parking = "Requested"
        elif valet.status == "Ready for Delivery":
            valet_parking = "Vehicle Ready"
        else:
            valet_parking= "Parked"
    
    checkin_list = frappe.get_all('Check In', filters={'client_id': client.name, 'check_in_type': 'Club Check-in'}, fields={'name', 'check_in_time'}, order_by="check_in_time desc")
    if checkin_list:
        checkin = checkin_list[0]
        check_in = checkin.check_in_time.date()
    
    food_list = frappe.get_all('Food Order Entry', filters={'client_id': client.name, 'date': today, 'order_status': ['in', {"Ordered","Ready"}]}, fields={'name', 'order_status'}, order_by="creation asc")
    if food_list:
        food = food_list[0]
        food_order = food.order_status
    
    group_class_list = frappe.get_all('Group Class Attendees', filters={'client_id': client.name, 'class_status':['in', {'Open','Scheduled'}]}, fields={'group_class_name', 'class_date'}, order_by="from_time asc")
    if group_class_list:
        gc = group_class_list[0]
        group_class = gc.class_date

    pt_list = frappe.get_all('Fitness Training Appointment', filters={'client_id': client.name, 'appointment_status':['in', {'Open','Scheduled'}]})
    if pt_list:
        fitness = len(pt_list)

  else:
    club_tour_list = frappe.get_all('Club Tour', filters={'client_id': client.name,'tour_status':['in', {'Pending','Scheduled'}]})
    if club_tour_list:
      club_tour = club_tour_list[0]
      club_tour_status = club_tour.tour_status
  
  spa_list = frappe.get_all('Spa Appointment', filters={'client_id': client.name, 'appointment_status':['in', {'Open','Scheduled'}]}, fields={'start_time'}, order_by="start_time asc")
  if spa_list:
      spa = spa_list[0]
      spa_next = spa.start_time.date()
 
  frappe.response["data"] = {
            'name': client.name,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'client_name': client.client_name,
            'status': client.status,
            'gender': client.gender,
            'birth_date': client.birth_date,
            'nationality': client.nationality,
            'qatar_id': client.qatar_id,
            'email': client.email,
            'mobile_no': client.mobile_no,
            'apply_membership': client.apply_membership,
            'mem_application': client.mem_application,
            'membership_status': client.membership_status,
            'member_id': client.member_id,
            'card_no' : client.card_no,
            'membership_id': client.membership_id,
            'customer_group': client.customer_group,
            'territory': client.territory ,
            'marital_status': client.marital_status,
            'image': client.image,
            'assigned_cec': client.assigned_to,
            'cec_mobile_no': cec_mobile_no,
            'primary_member': client.primary_member,
            'offers_notification': client.offers_notification,
            "Valet": valet_parking,
            "valet_id": valet_name,
            "checkin": check_in,
            "food_order": food_order,
            "group_class": group_class,
            "fitness": fitness,
            "spa": spa_next,
            "club_tour": club_tour_status,
            "mem_app_image": app_settings.membership_application,
            "club_tour_image": app_settings.club_tour,
            "pt_image": app_settings.pt_sessions,
            "group_class_image": app_settings.group_classes,
            "restaurant_image": app_settings.grams_table,
            "ios_version": app_settings.ios_version
  }
