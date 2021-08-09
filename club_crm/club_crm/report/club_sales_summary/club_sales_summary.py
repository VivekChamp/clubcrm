# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

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
	"label": "Type",
	"fieldname": "type",
	"fieldtype": "Data",
	"width": 150,
	"hidden": 1
	},
	{
	"label": "Online",
	"fieldname": "online",
	"fieldtype": "Check",
	"width": 30,
	"hidden": 1
	},
	{
	"label": "Document No",
	"fieldname": "document_no",
	"fieldtype": "Dynamic Link",
	"options":"type",
	"width": 175
	},
	{
	"label": "Client Name",
	"fieldname": "client_name",
	"fieldtype": "Data",
	"width": 350
	},
	{
	"label": "Description",
	"fieldname": "description",
	"fieldtype": "Data",
	"width": 250
	},
	{
	"label": "Amount",
	"fieldname": "in_amount",
	"fieldtype": "Currency",
	"width": 160
	}
	]
	return columns
	
def get_data(filters):
	data = []
	final_data = []
	mem_app_list = frappe.db.sql('''select
										ma.application_date as date,
										%s as type,
										ma.online_application as online,
										ma.name as document_no,
										ma.client_id as client_id,
										ma.first_name_1 as client_name,
										ma.membership_plan as description,
										ma.grand_total as in_amount
									from `tabMemberships Application` ma 
									where 
										ma.application_date between %s and %s and ma.docstatus = 1
									order by ma.application_date asc''',

									('Memberships Application',filters['from_date'],filters['to_date']), as_dict = True)

	ftr = frappe.db.sql('''select
								ftr.date as date,
								%s as type,
								%s as online,
								ftr.name as document_no,
								ftr.membership_status,
								ftr.client_id as client_id,
								ftr.client_name as client_name,
								ftr.fitness_package as description,
								ftr.price as in_amount
							from `tabFitness Training Request` ftr
							where ftr.date between %s and %s and ftr.payment_status="Paid"
							order by ftr.date asc''',

							('Fitness Training Request',1,filters['from_date'],filters['to_date']), as_dict = True)

	on_order = frappe.db.sql('''select
									ord.created_date as date,
									%s as type,
									ord.name as document_no,
									ord.membership_status,
									ord.client_id as client_id,
									ord.client_name as client_name, 
									ord.payment_method as in_payment_mode,
									ord.total_amount as in_amount
								from `tabOnline Order` ord
								where ord.created_date between %s and %s and ord.payment_status = "Paid"''',
								
								('Online Order',filters['from_date'],filters['to_date']), as_dict = True)

	cart = frappe.db.sql('''select
								ca.date as date,
								%s as type,
								ca.online as online,
								ca.name as document_no,
								ca.membership_status,
								ca.products_check,
								ca.client_id as client_id,
								ca.client_name as client_name,
								ca.sessions_check,
								ca.appointments_check 
							from `tabCart` ca
							where ca.date between %s and %s and ca.payment_status = "Paid"
							order by ca.date asc''',

							('Cart',filters['from_date'],filters['to_date']), as_dict = True)
	
	if 'type' in filters:
		if filters['type'] == 'Spa':
			for row in cart:
				if 'sessions_check' in row and row['sessions_check'] and 'appointments_check' in row and row['appointments_check']:
					appointments_total = 0.0
					sessions_total = 0.0
					appointment_list = frappe.get_all('Cart Appointment', filters={'parent': row['document_no'],'appointment_type': 'Spa Appointment'})
					if appointment_list:
						for appointment in appointment_list:
							appointments_total += frappe.db.get_value('Cart Appointment', appointment.name,'total_price')

					session_list = frappe.get_all('Cart Session', filters={'parent': row['document_no'], 'package_type': 'Spa'})
					if session_list:
						for session in session_list:
							sessions_total += frappe.db.get_value('Cart Session', session.name,'total_price')

					row['in_amount'] = appointments_total + sessions_total
					row['description'] = 'Spa Appointment + Spa Package'
					data.append(row)

				if 'sessions_check' in row and row['sessions_check'] and not row['appointments_check']:
					sessions_total = 0.0
					session_list = frappe.get_all('Cart Session', filters={'parent': row['document_no'], 'package_type': 'Spa'})
					if session_list:
						for session in session_list:
							sessions_total += frappe.db.get_value('Cart Session', session.name,'total_price')

					row['in_amount'] = sessions_total
					row['description'] = 'Spa Package'
					data.append(row)
						
				if 'appointments_check' in row and row['appointments_check'] and not row['sessions_check']:
					appointments_total = 0.0
					appointment_list = frappe.get_all('Cart Appointment', filters={'parent': row['document_no'],'appointment_type': 'Spa Appointment'})
					if appointment_list:
						for appointment in appointment_list:
							appointments_total += frappe.db.get_value('Cart Appointment', appointment.name,'total_price')

					row['in_amount'] = appointments_total
					row['description'] = 'Spa Appointment'
					data.append(row)

		if filters['type'] == 'Fitness':
			for row in cart:
				if 'sessions_check' in row and row['sessions_check'] and not row['appointments_check']:
					sessions_total = 0.0
					session_list = frappe.get_all('Cart Session', filters={'parent': row['document_no'], 'package_type': 'Fitness'})
					if session_list:
						for session in session_list:
							sessions_total += frappe.db.get_value('Cart Session', session.name,'total_price')

					row['in_amount'] = sessions_total
					row['description'] = 'PT Package'
					data.append(row)
			
			data += ftr
					
		if filters['type'] == 'Others':
			for row in cart:
				if 'sessions_check' in row and row['sessions_check'] and not row['appointments_check']:
					sessions_total = 0.0
					session_list = frappe.get_all('Cart Session', filters={'parent': row['document_no'], 'package_type': 'Club'})
					if session_list:
						for session in session_list:
							sessions_total += frappe.db.get_value('Cart Session', session.name,'total_price')

					row['in_amount'] = sessions_total
					row['description'] = 'Club Services'
					data.append(row)

		if filters['type'] == 'Retail':
			for row in cart:
				if row['products_check']:
					in_amount = frappe.db.get_value('Cart', row['document_no'],'net_total_products')
					if in_amount:
						row['in_amount'] = in_amount
						row['description'] = 'Retail Products'
					data.append(row)

		if filters['type'] == 'Membership':
			data += mem_app_list

	else:
		for row in cart:
			in_amount = frappe.db.get_value('Cart', row['document_no'],'grand_total')
			if in_amount:
				row['in_amount'] = in_amount
				row['description'] = 'Cart'
				data.append(row)

		data += ftr + mem_app_list

	for row in data:
		allow_by_membership_status = False
		allow_by_transaction_type = False

		if 'client_id' in row:
			row['membership_status'] = frappe.db.get_value('Client', row['client_id'], 'membership_status')
		if 'membership_status' in filters:
			if filters['membership_status'] == row['membership_status']:
				allow_by_membership_status = True
		else:
			allow_by_membership_status = True

		if 'transaction_type' in filters:
			if filters['transaction_type'] == 'Online' and row['online'] == 1:
				allow_by_transaction_type = True
			elif filters['transaction_type'] == 'Offline' and row['online'] ==0:
				allow_by_transaction_type = True
			else:
				allow_by_transaction_type = False
		else:
			allow_by_transaction_type = True

		if allow_by_membership_status and allow_by_transaction_type and row['in_amount'] != 0.0:
			final_data.append(row)

	return final_data