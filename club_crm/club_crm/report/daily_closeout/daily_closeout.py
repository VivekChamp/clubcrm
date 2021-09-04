# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	if filters:
		columns = get_column(filters)
		data = get_data(filters)
	return columns, data

def get_column(filters):
	columns = [
		{
			"label": "Amount",
			"fieldname": "in_amount",
			"fieldtype": "Currency",
			"width": 160
		}
	]
	if filters.get('report_type') == "By Payment Type":
		columns.insert(0,
			{
			"label": "Payment Type",
			"fieldname": "payment_type",
			"fieldtype": "Data",
			"width": 150
		})
	elif filters.get('report_type') == "By Category":
		columns.insert(0,
			{
			"label": "Category",
			"fieldname": "category",
			"fieldtype": "Data",
			"width": 150
		})
		# columns.insert(1,
		# 	{
		# 	"label": "Quantity",
		# 	"fieldname": "quantity",
		# 	"fieldtype": "Data",
		# 	"width": 100
		# })
	elif filters.get('report_type') == "By Transaction Type":
		columns.insert(0,
			{
			"label": "Transaction Type",
			"fieldname": "transaction_type",
			"fieldtype": "Data",
			"width": 150
		})
		# columns.insert(1,
		# 	{
		# 	"label": "Quantity",
		# 	"fieldname": "quantity",
		# 	"fieldtype": "Data",
		# 	"width": 100
		# })

	return columns

def get_data(filters):
	data = []
	final_data = []

	cart = frappe.db.sql ("""	select
										cart.name as document_no,
										cart.products_check,
										cart.sessions_check,
										cart.appointments_check,
										cart.online as online,
										pay.payment_date,
										pay.mode_of_payment,
										pay.paid_amount
									from `tabCart` cart
									left join `tabCart Payment` pay
										on cart.name = pay.parent
									where 
										cart.payment_status = %s and
										cart.date between %s and %s
									order by pay.payment_date asc""",
									('Paid', filters['from_date'], filters['to_date']), as_dict = True)
		
	mem_app = frappe.db.sql(""" select
										ma.online_application as online,
										pay.payment_date,
										pay.mode_of_payment,
										pay.paid_amount									
									from `tabMemberships Application` ma
									left join `tabCart Payment` pay
										on ma.name = pay.parent
									where
										ma.workflow_status = %s and
										pay.payment_date between %s and %s
									order by pay.payment_date asc""",

									('Complete', filters['from_date'], filters['to_date']), as_dict = True)

	ftr = frappe.db.sql("""		select
										pay.payment_date,
										pay.mode_of_payment,
										pay.paid_amount
									from `tabFitness Training Request` ftr
									left join `tabCart Payment` pay
										on ftr.name = pay.parent
									where
										ftr.payment_status = %s and
										pay.payment_date between %s and %s
									order by pay.payment_date asc""",

									('Paid', filters['from_date'], filters['to_date']), as_dict = True)

	on_order = frappe.db.sql("""select
										ord.created_date as payment_date, 
										ord.payment_method as mode_of_payment,
										ord.total_amount as paid_amount
									from `tabOnline Order` ord
									where
										ord.created_date between %s and %s and ord.payment_status = %s """,
									
									(filters['from_date'], filters['to_date'], 'Paid'), as_dict = True)
	
	if filters['report_type']=="By Category":
		spa_package = 0.0
		spa_p_qty = 0
		spa_appointment = 0.0
		spa_app_qty = 0
		pt_package = 0.0
		club_package = 0.0
		pt_qty = 0
		retail = 0.0
		ret_qty = 0
		mem_application = 0.0
		mem_qty = 0

		cart = frappe.db.sql ("""	select
										cart.name as document_no,
										cart.products_check,
										cart.sessions_check,
										cart.appointments_check,
										cart.online as online
									from `tabCart` cart
									where 
										cart.payment_status = %s and
										cart.date between %s and %s
									order by cart.date asc""",
									('Paid', filters['from_date'], filters['to_date']), as_dict = True)
		
		for row in cart:
			doc = frappe.get_doc('Cart', row.document_no)
			if doc.sessions_check:
				spa_sessions_total = 0.0
				pt_sessions_total = 0.0
				club_sessions_total = 0.0
				spa_session_list = frappe.get_all('Cart Session', filters={'parent': doc.name, 'package_type': 'Spa'})
				if spa_session_list:
					for session in spa_session_list:
						spa_sessions_total += frappe.db.get_value('Cart Session', session.name,'total_price')
						spa_package += spa_sessions_total
						# spa_p_qty += 1
				
				pt_session_list = frappe.get_all('Cart Session', filters={'parent': doc.name, 'package_type': 'Fitness'})
				if pt_session_list:
					for session in pt_session_list:
						pt_sessions_total += frappe.db.get_value('Cart Session', session.name,'total_price')
						pt_package += pt_sessions_total
						# pt_qty += 1

				club_session_list = frappe.get_all('Cart Session', filters={'parent': doc.name, 'package_type': 'Club'})
				if club_session_list:
					for session in club_session_list:
						club_sessions_total += frappe.db.get_value('Cart Session', session.name,'total_price')
						club_package += club_sessions_total
							
			if doc.appointments_check:
				appointments_total = 0.0
				appointment_list = frappe.get_all('Cart Appointment', filters={'parent': doc.name,'appointment_type': 'Spa Appointment'})
				if appointment_list:
					for appointment in appointment_list:
						appointments_total += frappe.db.get_value('Cart Appointment', appointment.name,'total_price')
						spa_appointment += appointments_total
						# spa_app_qty += 1
			
			if doc.products_check:
				in_amount = frappe.db.get_value('Cart', doc.name,'net_total_products')
				if in_amount:
					retail += in_amount
		
		for row in ftr:
			pt_package += row.paid_amount

		for row in mem_app:
			mem_application += row.paid_amount

		final_data.append({
			'category': 'Spa Appointments',
			'in_amount' : spa_appointment
		})
		final_data.append({
			'category': 'Spa Packages',
			'in_amount' : spa_package
		})
		final_data.append({
			'category': 'Fitness Packages',
			'in_amount' : pt_package
		})
		final_data.append({
			'category': 'Club Packages',
			'in_amount' : club_package
		})
		final_data.append({
			'category': 'Memberships',
			'in_amount' : mem_application
		})
		final_data.append({
			'category': 'Retail and Others',
			'in_amount' : retail
		})
	
		return final_data

	else:
		data = cart + mem_app + ftr
		if data:
			if filters['report_type']=="By Payment Type":
				mode_of_payment = frappe.get_all('Mode of Payment', filters={'enabled':1})
				if mode_of_payment:
					for pay in mode_of_payment:
						amount = 0.0
						for row in data:
							if row.mode_of_payment == pay.name:
								amount += row.paid_amount
						if amount > 0.0:
							pay['payment_type'] = pay.name
							pay['in_amount'] = amount
							final_data.append(pay)
					
					return final_data

			if filters['report_type']=="By Transaction Type":
				online_amount = 0.0
				offline_amount = 0.0
				qty_online = 0
				qty_offline = 0
				for row in data:
					if row.mode_of_payment == "Online Payment":
						online_amount += row.paid_amount
						qty_online += 1
					else:
						offline_amount += row.paid_amount
						qty_offline += 1

				final_data.append({
					'transaction_type': 'Online Payments',
					'quantity' : qty_online,
					'in_amount' : online_amount
					})
				
				final_data.append({
					'transaction_type': 'Offline Payments',
					'quantity' : qty_offline,
					'in_amount' : offline_amount
					})

			return final_data

