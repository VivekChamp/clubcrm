# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date, time
import calendar

def execute(filters=None):
	columns, data = [], []
	if filters:
		columns = get_column()
		data = get_data(filters)
	return columns, data

def get_column():
	columns = [
	{
	"label": "Date",
	"fieldname": "date",
	"fieldtype": "Date",
	"width": 100
	},
	{
	"label": "Staff Name",
	"fieldname": "staff_name",
	"fieldtype": "Data",
	"width": 110
	},
	{
	"label": "Doc ID",
	"fieldname": "document_id",
	"fieldtype": "Link",
	"options": "Spa Appointment",
	"width": 180
	},
	{
	"label": "Client Name",
	"fieldname": "client_name",
	"fieldtype": "Data",
	"width": 275
	},
	{
	"label": "Service Amount",
	"fieldname": "service_amount",
	"fieldtype": "Currency",
	"width": 160
	},
	{
	"label": "Commission %",
	"fieldname": "commission",
	"fieldtype": "Percent",
	"width": 120
	},
	{
	"label": "Commission Amount",
	"fieldname": "comm_amount",
	"fieldtype": "Currency",
	"width": 160
	}
	]
	return columns

def get_data(filters):
	data = []

	year = int(filters['year'])
	if 'date_range' in filters:
		if filters['date_range'] == "Month":
			month = filters['month']
			month_number = int(datetime.strptime(month, '%B').month)
			last_day = calendar.monthrange(year, month_number)[1]

			start_date = datetime(year, month_number, 1)
			start = start_date.date()
			end_date = datetime(year, month_number, last_day)
			end = end_date.date()

		elif filters['date_range'] == "Custom Range":
			start = getdate(filters['from_date'])
			end = getdate( filters['to_date'])

	if 'service_staff' in filters:
		appointments_list = frappe.db.get_list('Spa Appointment', filters=[['appointment_date', 'between', [start, end]], ['payment_status', '=', 'Paid'], ['service_staff', '=', filters['service_staff']], ['appointment_status', 'in', {'Complete', 'No Show'}]], fields=['name as document_id', 'appointment_date as date', 'client_name', 'service_staff as staff_name'], order_by='appointment_date asc')
	else:
		appointments_list = frappe.db.get_list('Spa Appointment', filters=[['appointment_date', 'between', [start, end]], ['payment_status', '=', 'Paid'], ['appointment_status', 'in', {'Complete', 'No Show'}]], fields=['name as document_id', 'appointment_date as date', 'client_name', 'service_staff as staff_name'], order_by='appointment_date asc')

	if appointments_list:
		for appointments in appointments_list:
			commission_percentage = 0.0
			appointment = frappe.get_doc('Spa Appointment', appointments.document_id)
			spa_service = frappe.get_doc('Spa Services', appointment.spa_service)
			staff = frappe.get_doc('Service Staff', appointment.service_staff)
			if staff.spa_service_assignment:
				for row in staff.spa_service_assignment:
					if row.spa_group == spa_service.spa_group:
						commission_percentage = row.commission
			appointments['commission'] = commission_percentage

			if spa_service.session_type == "Standard":
				if appointment.cart:
					cart = frappe.get_doc('Cart', appointment.cart)
					if cart.cart_appointment:
						service_amount = 0.0
						for row in cart.cart_appointment:
							if row.appointment_id == appointment.name:
								service_amount += row.total_price
				else:
					service_amount = appointment.net_total
			
			elif spa_service.session_type == "Complimentary":
				net_total = spa_service.regular_price_reference
				discount_amount = 0.0
				if appointment.membership_status == "Member":
					client = frappe.get_doc('Client', appointment.client_id)
					if client.membership_history:
						for row in client.membership_history:
							if row.status == "Active":
								mem = frappe.get_doc('Memberships', row.membership)
								discount_amount = mem.spa_discount
				
				service_amount = float(net_total) - (float(net_total) * float(discount_amount)/100)
			
			appointments['service_amount'] = service_amount

			commission_amount = float(service_amount) * float(commission_percentage)/100
			appointments['comm_amount'] = commission_amount

			data.append(appointments)

	return data		

@frappe.whitelist()
def month():
	year = 2021
	months = 'June'
	month_number = datetime.strptime(months, '%B').month
	last_day = calendar.monthrange(year, month_number)[1]

	start_date = datetime(year, month_number, 1)
	start = start_date.date()
	end_date = datetime(year, month_number, last_day)
	end = end_date.date()

	appointment_lists = frappe.db.sql('''select
											spa.name as document_id,
											spa.appointment_date as date,
											spa.client_id as client_id
										from
											`tabSpa Appointment` spa
										where 
	 										spa.appointment_date between %s and %s
											and spa.payment_status LIKE %s
											and (spa.appointment_status LIKE %s OR spa.appointment_status LIKE %s ) ''',
										(start, end, "Paid", "Complete", "No Show" ), as_dict = True)

	app_list = frappe.db.get_list('Spa Appointment', filters=[['appointment_date', 'between', [start, end]], ['payment_status', '=', 'Paid'], ['appointment_status', 'in', {'Complete', 'No Show'}]])
		
	return app_list, appointment_lists