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
	"label": "Description",
	"fieldname": "description",
	"fieldtype": "Data",
	"width": 300
	},
	{
	"label": "Paid Visits",
	"fieldname": "paid_visits",
	"fieldtype": "Data",
	"width": 120
	},
	{
	"label": "Unpaid Visits",
	"fieldname": "unpaid_visits",
	"fieldtype": "Data",
	"width": 120
	},
	{
	"label": "Total Visits",
	"fieldname": "total_visits",
	"fieldtype": "Data",
	"width": 120
	},
	{
	"label": "Percentage",
	"fieldname": "percentage",
	"fieldtype": "Percentage",
	"width": 120
	}
	]
	return columns

def get_data(filters):
	data = []
	final_data = []

	if 'service_staff' in filters:
		if filters['report_type'] == "By Packages":
			if filters['package_type'] ==  'All Packages':
				club_packages = frappe.get_all('Club Packages', fields=['name', 'package_type'])
			else:
				club_packages = frappe.get_all('Club Packages', filters={'package_type': filters['package_type']}, fields=['name', 'package_type'])
			
			if club_packages:
				for package in club_packages:
					if package.package_type == 'Fitness':
						pt_app_paid = frappe.db.sql("""select
													pt.name, pt.session_name, pt.fitness_service, pt.service_staff, sess.package_name			
												from `tabFitness Training Appointment` pt
												left join `tabClient Sessions` sess
													on pt.session_name = sess.name
												where
													sess.package_name = %s
													and pt.service_staff = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.payment_status = %s
													and pt.appointment_date between %s and %s
													""",
												(package.name, filters['service_staff'], 'Completed', 'No Show', 'Paid', filters['from_date'], filters['to_date']), as_dict = True)
						
						pt_app_unpaid = frappe.db.sql("""select
													pt.name, pt.session_name, pt.fitness_service, pt.service_staff, sess.package_name			
												from `tabFitness Training Appointment` pt
												left join `tabClient Sessions` sess
													on pt.session_name = sess.name
												where 
													sess.package_name = %s
													and pt.service_staff = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.payment_status = %s
													and pt.appointment_date between %s and %s
													""",
												(package.name, filters['service_staff'], 'Completed', 'No Show', 'Not Paid', filters['from_date'], filters['to_date']), as_dict = True)
						
						package['description'] = package.name
						if pt_app_paid:
							package['paid_visits'] = len(pt_app_paid)
						else:
							package['paid_visits'] = 0

						if pt_app_unpaid:
							package['unpaid_visits'] = len(pt_app_unpaid)
						else:
							package['unpaid_visits'] = 0
						package['total_visits'] = package['paid_visits'] + package['unpaid_visits']
						data.append(package)

					if package.package_type == 'Spa':
						spa_paid = frappe.db.sql("""select
													spa.name, spa.session_name, spa.spa_service, spa.service_staff, sess.package_name			
												from `tabSpa Appointment` spa
												left join `tabClient Sessions` sess
													on spa.session_name = sess.name
												where 
													sess.package_name = %s
													and spa.service_staff = %s
													and (spa.appointment_status = %s or spa.appointment_status = %s)
													and spa.payment_status = %s
													and spa.appointment_date between %s and %s
													""",
												(package.name, filters['service_staff'], 'Complete', 'No Show', 'Paid', filters['from_date'], filters['to_date']), as_dict = True)
						
						spa_unpaid = frappe.db.sql("""select
													spa.name, spa.session_name, spa.spa_service, spa.service_staff, sess.package_name			
												from `tabSpa Appointment` spa
												left join `tabClient Sessions` sess
													on spa.session_name = sess.name
												where 
													sess.package_name = %s
													and spa.service_staff = %s
													and (spa.appointment_status = %s or spa.appointment_status = %s)
													and spa.payment_status = %s
													and spa.appointment_date between %s and %s
													""",
												(package.name, filters['service_staff'], 'Complete', 'No Show', 'Not Paid', filters['from_date'], filters['to_date']), as_dict = True)

						package['description'] = package.name
						if spa_paid:
							package['paid_visits'] = len(spa_paid)
						else:
							package['paid_visits'] = 0

						if spa_unpaid:
							package['unpaid_visits'] = len(spa_unpaid)
						else:
							package['unpaid_visits'] = 0
						package['total_visits'] = package['paid_visits'] + package['unpaid_visits']
						data.append(package)
				
				total = 0
				for row in data:
					total += row['total_visits']
					
				for row in data:
					if row['total_visits'] != 0:
						row['percentage'] = round((row['total_visits'] / total) * 100, 2)
						final_data.append(row)

				return final_data
		
		elif filters['report_type'] == "By Services":
			if filters['service_type'] == "Spa":
				spa_services = frappe.get_all('Spa Services')
				for spa_service in spa_services:
					spa_paid = frappe.db.sql("""select
													spa.name, spa.spa_service, spa.service_staff	
													from `tabSpa Appointment` spa
													where
														spa.spa_service = %s
														and spa.service_staff = %s
														and (spa.appointment_status = %s or spa.appointment_status = %s)
														and spa.payment_status = %s
														and spa.appointment_date between %s and %s
														""",
													(spa_service.name, filters['service_staff'], 'Complete', 'No Show', 'Paid', filters['from_date'], filters['to_date']), as_dict = True)
					
					spa_unpaid = frappe.db.sql("""select
													spa.name, spa.spa_service, spa.service_staff	
													from `tabSpa Appointment` spa
													where
														spa.spa_service = %s
														and spa.service_staff = %s
														and (spa.appointment_status = %s or spa.appointment_status = %s)
														and spa.payment_status = %s
														and spa.appointment_date between %s and %s
														""",
													(spa_service.name, filters['service_staff'], 'Complete', 'No Show', 'Not Paid', filters['from_date'], filters['to_date']), as_dict = True)

					spa_service['description'] = spa_service.name
					if spa_paid:
						spa_service['paid_visits'] = len(spa_paid)
					else:
						spa_service['paid_visits'] = 0

					if spa_unpaid:
						spa_service['unpaid_visits'] = len(spa_unpaid)
					else:
						spa_service['unpaid_visits'] = 0
					spa_service['total_visits'] = spa_service['paid_visits'] + spa_service['unpaid_visits']
					data.append(spa_service)

				total = 0
				for row in data:
					total += row['total_visits']
					
				for row in data:
					if row['total_visits'] != 0:
						row['percentage'] = round((row['total_visits'] / total) * 100, 2)
						final_data.append(row)

				return final_data
				
			if filters['service_type'] == "Fitness":
				fitness_services = frappe.get_all('Fitness Services')
				for fitness_service in fitness_services:
					pt_paid = frappe.db.sql("""select
												pt.name, pt.fitness_service, pt.service_staff	
												from `tabFitness Training Appointment` pt
												where
													pt.fitness_service = %s
													and pt.service_staff = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.payment_status = %s
													and pt.appointment_date between %s and %s
													""",
												(fitness_service.name, filters['service_staff'], 'Completed', 'No Show',  'Paid', filters['from_date'], filters['to_date']), as_dict = True)
				
					pt_unpaid = frappe.db.sql("""select
												pt.name, pt.fitness_service, pt.service_staff	
												from `tabFitness Training Appointment` pt
												where
													pt.fitness_service = %s
													and pt.service_staff = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.payment_status = %s
													and pt.appointment_date between %s and %s
													""",
												(fitness_service.name, filters['service_staff'], 'Completed', 'No Show',  'Not Paid', filters['from_date'], filters['to_date']), as_dict = True)
					
					fitness_service['description'] = fitness_service.name
					if pt_paid:
						fitness_service['paid_visits'] = len(pt_paid)
					else:
						fitness_service['paid_visits'] = 0

					if pt_unpaid:
						fitness_service['unpaid_visits'] = len(pt_unpaid)
					else:
						fitness_service['unpaid_visits'] = 0
					fitness_service['total_visits'] = fitness_service['paid_visits'] + fitness_service['unpaid_visits']
					data.append(fitness_service)

				total = 0
				for row in data:
					total += row['total_visits']
					
				for row in data:
					if row['total_visits'] != 0:
						row['percentage'] = round((row['total_visits'] / total) * 100, 2)
						final_data.append(row)

				return final_data
	
	else:
		if filters['report_type'] == "By Packages":
			if filters['package_type'] ==  'All Packages':
				club_packages = frappe.get_all('Club Packages', fields=['name', 'package_type'])
			elif filters['package_type'] ==  'Spa':
				club_packages = frappe.get_all('Club Packages', filters={'package_type': ['in', ['Spa', 'Club']]}, fields=['name', 'package_type'])
			elif filters['package_type'] ==  'Fitness':
				club_packages = frappe.get_all('Club Packages', filters={'package_type': ['in', ['Fitness', 'Club']]}, fields=['name', 'package_type'])

			if club_packages:
				for package in club_packages:
					if package.package_type == 'Fitness':
						pt_app_paid = frappe.db.sql("""select
													pt.name, pt.session_name, pt.fitness_service, pt.service_staff, sess.package_name			
												from `tabFitness Training Appointment` pt
												left join `tabClient Sessions` sess
													on pt.session_name = sess.name
												where 
													sess.package_name = %s
													and pt.payment_status = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.appointment_date between %s and %s
													""",
												(package.name, 'Paid', 'Completed', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)
						
						pt_app_unpaid = frappe.db.sql("""select
													pt.name, pt.session_name, pt.fitness_service, pt.service_staff, sess.package_name			
												from `tabFitness Training Appointment` pt
												left join `tabClient Sessions` sess
													on pt.session_name = sess.name
												where 
													sess.package_name = %s
													and pt.payment_status = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.appointment_date between %s and %s
													""",
												(package.name, 'Not Paid', 'Completed', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)
						
						package['description'] = package.name
						if pt_app_paid:
							package['paid_visits'] = len(pt_app_paid)
						else:
							package['paid_visits'] = 0

						if pt_app_unpaid:
							package['unpaid_visits'] = len(pt_app_unpaid)
						else:
							package['unpaid_visits'] = 0
						package['total_visits'] = package['paid_visits'] + package['unpaid_visits']
						data.append(package)

					if package.package_type == 'Spa':
						spa_paid = frappe.db.sql("""select
													spa.name, spa.session_name, spa.spa_service, spa.service_staff, sess.package_name			
												from `tabSpa Appointment` spa
												left join `tabClient Sessions` sess
													on spa.session_name = sess.name
												where 
													sess.package_name = %s
													and spa.payment_status = %s
													and (spa.appointment_status = %s or spa.appointment_status = %s)
													and spa.appointment_date between %s and %s
													""",
												(package.name, 'Paid', 'Complete', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)
						
						spa_unpaid = frappe.db.sql("""select
													spa.name, spa.session_name, spa.spa_service, spa.service_staff, sess.package_name			
												from `tabSpa Appointment` spa
												left join `tabClient Sessions` sess
													on spa.session_name = sess.name
												where 
													sess.package_name = %s
													and spa.payment_status = %s
													and (spa.appointment_status = %s or spa.appointment_status = %s)
													and spa.appointment_date between %s and %s
													""",
												(package.name, 'Not Paid', 'Complete', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)

						package['description'] = package.name
						if spa_paid:
							package['paid_visits'] = len(spa_paid)
						else:
							package['paid_visits'] = 0

						if spa_unpaid:
							package['unpaid_visits'] = len(spa_unpaid)
						else:
							package['unpaid_visits'] = 0
						package['total_visits'] = package['paid_visits'] + package['unpaid_visits']
						data.append(package)
				
				total = 0
				for row in data:
					total += row['total_visits']
					
				for row in data:
					if row['total_visits'] != 0:
						row['percentage'] = round((row['total_visits'] / total) * 100, 2)
						final_data.append(row)

				return final_data
		
		elif filters['report_type'] == "By Services":
			if filters['service_type'] == "Spa":
				spa_services = frappe.get_all('Spa Services')
				for spa_service in spa_services:
					spa_paid = frappe.db.sql("""select
													spa.name, spa.spa_service, spa.service_staff	
													from `tabSpa Appointment` spa
													where
														spa.spa_service = %s
														and spa.payment_status = %s
														and (spa.appointment_status = %s or spa.appointment_status = %s)
														and spa.appointment_date between %s and %s
														""",
													(spa_service.name, 'Paid', 'Complete', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)
					
					spa_unpaid = frappe.db.sql("""select
													spa.name, spa.spa_service, spa.service_staff	
													from `tabSpa Appointment` spa
													where
														spa.spa_service = %s
														and spa.payment_status = %s
														and (spa.appointment_status = %s or spa.appointment_status = %s)
														and spa.appointment_date between %s and %s
														""",
													(spa_service.name, 'Not Paid', 'Complete', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)

					spa_service['description'] = spa_service.name
					if spa_paid:
						spa_service['paid_visits'] = len(spa_paid)
					else:
						spa_service['paid_visits'] = 0

					if spa_unpaid:
						spa_service['unpaid_visits'] = len(spa_unpaid)
					else:
						spa_service['unpaid_visits'] = 0
					spa_service['total_visits'] = spa_service['paid_visits'] + spa_service['unpaid_visits']
					data.append(spa_service)

				total = 0
				for row in data:
					total += row['total_visits']
					
				for row in data:
					if row['total_visits'] != 0:
						row['percentage'] = round((row['total_visits'] / total) * 100, 2)
						final_data.append(row)

				return final_data
				
			if filters['service_type'] == "Fitness":
				fitness_services = frappe.get_all('Fitness Services')
				for fitness_service in fitness_services:
					pt_paid = frappe.db.sql("""select
												pt.name, pt.fitness_service, pt.service_staff	
												from `tabFitness Training Appointment` pt
												where
													pt.fitness_service = %s
													and pt.payment_status = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.appointment_date between %s and %s
													""",
												(fitness_service.name, 'Paid', 'Completed', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)
				
					pt_unpaid = frappe.db.sql("""select
												pt.name, pt.fitness_service, pt.service_staff	
												from `tabFitness Training Appointment` pt
												where
													pt.fitness_service = %s
													and pt.payment_status = %s
													and (pt.appointment_status = %s or pt.appointment_status = %s)
													and pt.appointment_date between %s and %s
													""",
												(fitness_service.name, 'Not Paid', 'Completed', 'No Show', filters['from_date'], filters['to_date']), as_dict = True)
					
					fitness_service['description'] = fitness_service.name
					if pt_paid:
						fitness_service['paid_visits'] = len(pt_paid)
					else:
						fitness_service['paid_visits'] = 0

					if pt_unpaid:
						fitness_service['unpaid_visits'] = len(pt_unpaid)
					else:
						fitness_service['unpaid_visits'] = 0
					fitness_service['total_visits'] = fitness_service['paid_visits'] + fitness_service['unpaid_visits']
					data.append(fitness_service)

				total = 0
				for row in data:
					total += row['total_visits']
					
				for row in data:
					if row['total_visits'] != 0:
						row['percentage'] = round((row['total_visits'] / total) * 100, 2)
						final_data.append(row)

				return final_data