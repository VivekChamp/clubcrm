# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import math
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
	"label": "Staff Name",
	"fieldname": "staff_name",
	"fieldtype": "Data",
	"width": 120
	},
	{
	"label": "PT Count (Hours)",
	"fieldname": "pt_count",
	"fieldtype": "Data",
	"width": 120
	},
	{
	"label": "GX Count (Hours)",
	"fieldname": "gx_count",
	"fieldtype": "Data",
	"width": 120
	},
	{
	"label": "Others (Hours)",
	"fieldname": "ot_count",
	"fieldtype": "Data",
	"width": 120
	},
	{
	"label": "PT Commissions",
	"fieldname": "pt_commission",
	"fieldtype": "Currency",
	"width": 150
	},
	{
	"label": "GX Commissions",
	"fieldname": "gc_commission",
	"fieldtype": "Currency",
	"width": 150
	},
	{
	"label": "Other Commissions",
	"fieldname": "other_commission",
	"fieldtype": "Currency",
	"width": 150,
	"default": 0.0
	},
	{
	"label": "Total Commission",
	"fieldname": "total_commission",
	"fieldtype": "Currency",
	"width": 150
	}
	]
	return columns

def get_data(filters):
	data = []
	final_data = []

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
		staff_list = frappe.get_all('Service Staff', filters={'name': filters['service_staff']})
	else:
		staff_list = frappe.db.get_list('Service Staff', filters=[['fitness_check', '=', 1]], fields=['name'])

	settings = frappe.get_doc('Fitness Training Settings')
	if staff_list:
		for staff in staff_list:
			pt_count = 0.0
			ot_count = 0.0
			other_commission = 0.0
			service_staff = frappe.get_doc('Service Staff', staff.name)
			if service_staff.fitness_service_assignment:
				for services in service_staff.fitness_service_assignment:
					if services.commission_applicable:
						appointments_list = frappe.db.get_list('Fitness Training Appointment', filters=[['fitness_service', '=', services.fitness_package], ['appointment_date', 'between', [start, end]], ['payment_status', '=', 'Paid'], ['service_staff', '=', staff.name], ['appointment_status', 'in', {'Completed', 'No Show'}]], fields=['name', 'fitness_service'])
					
						if services.commission_type == "Standard":
							if appointments_list:
								for appointments in appointments_list:
									pt_service = frappe.get_doc('Fitness Services', appointments.fitness_service)
									if pt_service.session_for == "Single":
										pt_count += settings.single_session
									elif pt_service.session_for == "Couple":
										pt_count += settings.couple_session
						
						elif services.commission_type == "Custom":
							if appointments_list:
								for appointments in appointments_list:
									other_commission += services.commission_amount
									ot_count += 1
			
			staff['staff_name']= staff.name
			staff['pt_count'] = pt_count
			staff['ot_count'] = ot_count
			staff['other_commission'] = other_commission
			
			gc = []
			gc_list = frappe.db.get_list('Group Class', filters=[['class_date', 'between', [start, end]], ['trainer_name', '=', staff.name], ['class_status', '=', 'Completed']], fields=['count(name) as gx_count'], group_by='trainer_name')
			if gc_list:
				for group_class in gc_list:
					group_class_attendee = frappe.get_all('Group Class Attendees', filters={'group_class': group_class.name, 'attendee_status': 'Complete' })
					if group_class_attendee:
						if len(group_class_attendee) >= 3:
							gc.append(group_class)

			staff['gx_count'] = len(gc)

			data.append(staff)
			
		for row in data:
			row['gc_commission'] = float(row['gx_count']) * float(settings.group_class_rate)

			pt = calculate_pt(row['pt_count'], row['gx_count'])
			row['pt_commission'] = pt

			row['total_commission'] = row['gc_commission'] + row['pt_commission'] + row['other_commission']
			
			final_data.append(row)

	return final_data		

def month():
	year = 2021
	months = 'July'
	month_number = datetime.strptime(months, '%B').month
	last_day = calendar.monthrange(year, month_number)[1]

	start_date = datetime(year, month_number, 1)
	start = start_date.date()
	end_date = datetime(year, month_number, last_day)
	end = end_date.date()

	staff_list = frappe.db.get_list('Service Staff', filters=[['fitness_check', '=', 1]], fields=['name'])
	for staff in staff_list:
		gc_list = frappe.db.get_list('Group Class', filters=[['class_date', 'between', [start, end]], ['trainer_name', '=', 'Jatinder'], ['class_status', '=', 'Completed']], fields=['count(name) as gc_count'], group_by='trainer_name')
		for gc in gc_list:
			return type(gc.gc_count)


@frappe.whitelist()
def calculate_pt(pt_count, gx_count):
	total_count = pt_count + gx_count
	scale = {(0, 30): 40, (30, 60): 60, (60, 90): 80, (90, 120): 100, (120, 150): 120, (150, math.inf): 140}
	hours_worked = total_count
	
	decimal_rate = next(rate for (lower, upper), rate in scale.items() if lower <= hours_worked and upper >= hours_worked)

	decimal_end = hours_worked - int(hours_worked)
	end_pay = decimal_end * decimal_rate

	# Use an integer for ease of calculation
	hours_worked = int(hours_worked)
	hours_paid_for = 0

	# Beginning total pay is just the decimal "ending"
	total_pay = end_pay

	while hours_paid_for < hours_worked:
    	# Find the rate for the current bucket of hours
		rate_filter = (rate for (lower, upper), rate in scale.items() if lower <= hours_paid_for and hours_paid_for < upper)
		current_level = next(rate_filter)
		total_pay += current_level
		hours_paid_for += 1

	total_session = total_pay

	scale_1 = {(0, 30): 40, (30, 60): 60, (60, 90): 80, (90, 120): 100, (120, 150): 120, (150, math.inf): 140}
	hours_worked_1 = gx_count

	decimal_rate_1 = next(rate for (lower, upper), rate in scale_1.items() if lower <= hours_worked_1 and upper >= hours_worked_1)

	decimal_end_1 = hours_worked_1 - int(hours_worked_1)
	end_pay_1 = decimal_end_1 * decimal_rate_1

	# Use an integer for ease of calculation
	hours_worked_1 = int(hours_worked_1)
	hours_paid_for_1 = 0

	# Beginning total pay is just the decimal "ending"
	total_pay_1 = end_pay_1

	while hours_paid_for_1 < hours_worked_1:
    	# Find the rate for the current bucket of hours
		rate_filter = (rate for (lower, upper), rate in scale_1.items() if lower <= hours_paid_for_1 and hours_paid_for_1 < upper)
		current_level = next(rate_filter)
		total_pay_1 += current_level
		hours_paid_for_1 += 1

	total_gc = total_pay_1
			
	commission_from_pt = total_session - total_gc

	return commission_from_pt