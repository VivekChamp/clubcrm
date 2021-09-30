# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	columns = [
		_("Client Name") + ":Data:250",
		_("Mobile No") + ":Data:100",
		_("Spa Service") + ":Data:200",
		_("Spa Therapist") + ":Data:150",
		_("Amount") + ":Currency:120"
	]

	if filters.get('date_type') == "Booking Date":
		columns.insert(0, _("Booking Date") + ":Date:120")
	elif filters.get('date_type') == "Appointment Date":
		columns.insert(0, _("Appointment Date") + ":Date:140")
	
	return columns

def get_data(filters):
	conditions = get_conditions(filters)

	if filters.get('date_type') == "Booking Date":
		query = frappe.db.sql("""select
								spa.booking_date,
								spa.client_name,
								spa.mobile_no,
								spa.spa_service,
								spa.service_staff
							
							from `tabSpa Appointment` spa
							left join `tabCart Appointment` cart on cart.appointment_id = spa.name

							where spa.docstatus<2 %s """ % 
							conditions, filters, as_dict=1)
	if filters.get('date_type') == "Appointment Date":
		query = frappe.db.sql("""select
								spa.appointment_date,
								spa.client_name,
								spa.mobile_no,
								spa.spa_service,
								spa.service_staff,
								cart.total_price
							
							from `tabSpa Appointment` spa
							left join `tabCart Appointment` cart on cart.appointment_id = spa.name

							where spa.docstatus<2 %s """ % 
							conditions, filters, as_dict=1)
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get('gender'): conditions += " and spa.gender = %(gender)s"
	if filters.get('membership_status'): conditions += "  and spa.membership_status = %(membership_status)s"
	if filters.get('spa_service'): conditions += " and spa.spa_service = %(spa_service)s"
	if filters.get('spa_category'): conditions += " and spa.spa_category = %(spa_category)s"
	if filters.get('service_staff'): conditions += " and spa.service_staff = %(service_staff)s"
	if filters.get('club_room'): conditions += " and spa.club_room = %(club_room)s"

	return conditions

