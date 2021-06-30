from __future__ import unicode_literals
import frappe
from datetime import date
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_appointments(client_id):
    spa= frappe.get_all('Spa Appointment', filters={'client_id':client_id,'docstatus':1,'status':'Open'}, fields=['name','spa_item','duration','appointment_date','appointment_time','rate','payment_status','spa_therapist'])
    group_class= frappe.get_all('Group Class Attendees', filters={'client_id':client_id,'docstatus':1,'class_status':'Open'}, fields=['name','group_class_name','trainer_name','class_status','from_time','to_time'])
    frappe.local.response["message"] ={
                "Spa Booking": spa,
                "Group Class":group_class,
                "Fitness Training": 'will be added soon here',
                "Grams Reservation": 'will be added soon here',
                "Online Order": 'will be added soon here'
                }

@frappe.whitelist()
def get_app_members(member_id):
    mem = frappe.get_all('Member Benefits', filters={'member_id':member_id}, fields=['*'])
    if mem:
        for d in mem:
            client_id= d.client_id
            client= frappe.get_doc('Client', client_id)
            spa= frappe.get_all('Spa Appointment', filters={'client_id':client_id,'docstatus':1,'status':'Open'}, fields=['name','spa_item','duration','appointment_date','appointment_time','rate','payment_status','spa_therapist'])
            group_class= frappe.get_all('Group Class Attendees', filters={'client_id':client_id,'docstatus':1,'class_status':'Open'}, fields=['name','group_class_name','trainer_name','class_status','from_time','to_time'])
            frappe.local.response["message"] ={
                "client_details": client,
                "spa_booking": spa,
                "group_class":group_class,
                "fitness_training": 'will be added soon here',
                "grams_reservation": 'will be added soon here',
                "online_order": 'will be added soon here'
                }