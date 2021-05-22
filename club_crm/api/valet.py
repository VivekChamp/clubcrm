import frappe
import datetime
from frappe.utils import now_datetime
from frappe.utils import escape_html
from frappe import throw, msgprint, _

def get_vehicle_vehicleno(vehicle_no):
    vehicle = frappe.get_all('Valet Parking', filters={'vehicle_no': vehicle_id, 'status': 'Parked'}, fields=['name','date','client_id','client_name','membership_status','membership_id','vehicle_no','vehicle_type','location','parking_time','valet_staff'])
    frappe.response["message"] =  vehicle

@frappe.whitelist()
def get_parked_vehicle():
    parked_vehicle = frappe.get_all('Valet Parking', filters={'status': 'Parked'}, fields=['name','date','client_id','client_name','membership_status','member_id','vehicle_no','vehicle_type','location','status','parking_time','valet_staff'])
    if parked_vehicle:
        frappe.response["message"] =  {
            'status' : 1,
            'parked_vehicles': parked_vehicle
        }
    else:
        frappe.response['message'] = {
            'status': 0
        }

@frappe.whitelist()
def get_requested_vehicle():
    requested_vehicle = frappe.get_all('Valet Parking', filters={'status':'Requested for Delivery'}, fields=['name','date','client_id','client_name','membership_status','member_id','vehicle_no','vehicle_type','location','status','parking_time','delivery_request_time','valet_staff'])
    ready_vehicle = frappe.get_all('Valet Parking', filters={'status': 'Ready for Delivery'}, fields=['name','date','client_id','client_name','membership_status','member_id','vehicle_no','vehicle_type','location','status','parking_time','delivery_request_time','delivery_time','valet_staff'])
    frappe.response["message"] = {
        "Requested Vehicles":requested_vehicle,
        "Ready for Delivery":ready_vehicle
    }

@frappe.whitelist()
def new_vehicle(client_id,vehicle_no,vehicle_type,location):
    user = frappe.get_doc('User',frappe.session.user)
    doc = frappe.get_doc({
        'doctype': 'Valet Parking',
        'client_id': client_id,
        'status': "Parked",
        'vehicle_no': vehicle_no,
        'vehicle_type': vehicle_type,
        'location': location,
        'valet_user': user.email
        })
    doc.save()
    frappe.response["message"] = {
        "Name": doc.name,
        "Status":"Vehicle has been parked",
        "Parked by": doc.valet_staff
        }

@frappe.whitelist()
def request_vehicle(valet_name):
    doc = frappe.get_doc('Valet Parking',valet_name)
    if doc.status=="Parked":
        doc.status = "Requested for Delivery"
        doc.delivery_request_time = now_datetime()
        doc.save()
        frappe.response["message"] = {
            "Success":1,
            "Status":"Vehicle has been requested for delivery"
        }
    else:
        frappe.response["message"] = {
            "Success":0,
            "Status":"Vehicle is not parked"
        }

@frappe.whitelist()
def ready_vehicle(valet_name):
    doc = frappe.get_doc('Valet Parking',valet_name)
    if doc.status=="Requested for Delivery":
        doc.status = "Ready for Delivery"
        doc.ready_time = now_datetime()
        doc.save()
        frappe.response["message"] = {
            "Success":1,
            "Status":"Vehicle is ready for delivery"
        }
    else:
        frappe.response["message"] = {
            "Success":0,
            "Status":"Vehicle has not been requested"
        }


@frappe.whitelist()
def deliver_vehicle(valet_name):
    doc = frappe.get_doc('Valet Parking',valet_name)
    if doc.status=="Ready for Delivery":
        doc.status = "Delivered"
        doc.delivery_time = now_datetime()
        doc.save()
        frappe.response["message"] = {
            "Success":1,
            "Status":"Vehicle is delivered"
        }
    else:
        frappe.response["message"] = {
            "Success":0,
            "Status":"Vehicle is not ready for delivery"
        }
