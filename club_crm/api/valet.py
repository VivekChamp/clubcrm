import frappe
import datetime
from frappe.utils import now_datetime
from frappe.utils import escape_html
from frappe import throw, msgprint, _

def get_vehicle_vehicleno(vehicle_no):
    vehicle = frappe.get_all('Valet Parking', filters={'vehicle_no': vehicle_id, 'status': 'Parked'}, fields=['name','date','client_id','client_name','membership_status','membership_id','vehicle_no','vehicle_type','location','parking_time','modified_by'])
    frappe.response["message"] =  vehicle

@frappe.whitelist()
def get_parked_vehicle():
    parked_vehicle = frappe.get_all('Valet Parking', filters={'status': 'Parked'}, fields=['name','date','client_id','client_name','membership_status','membership_id','vehicle_no','vehicle_type','location','status','parking_time','modified_by'])
    frappe.response["message"] =  parked_vehicle

@frappe.whitelist()
def get_requested_vehicle():
    requested_vehicle = frappe.get_all('Valet Parking', filters={'status':'Requested for Delivery'}, fields=['name','date','client_id','client_name','membership_status','membership_id','vehicle_no','vehicle_type','location','status','parking_time','delivery_request_time','modified_by'])
    ready_vehicle = frappe.get_all('Valet Parking', filters={'status': 'Ready for Delivery'}, fields=['name','date','client_id','client_name','membership_status','membership_id','vehicle_no','vehicle_type','location','status','parking_time','delivery_request_time','delivery_time','modified_by'])
    frappe.response["message"] = {
        "Requested Vehicles":requested_vehicle,
        "Ready for Delivery":ready_vehicle
    }

@frappe.whitelist()
def new_vehicle(client_id,vehicle_no,vehicle_type,location):
    doc = frappe.get_doc({
        'doctype': 'Valet Parking',
        #'date': date,
        'client_id': client_id,
        #'client_name': client_name,
        #parking_time': parking_time,
        'status': "Parked",
        'vehicle_no': vehicle_no,
        'vehicle_type': vehicle_type,
        'location': location
        })
    doc.insert()
    doc.submit()
    frappe.response["message"] = {
        "Name": doc.name,
        "Status":"Vehicle has been parked",
        "Parked by": doc.owner
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
