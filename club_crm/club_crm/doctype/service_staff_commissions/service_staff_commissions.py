# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import math
import calendar
import datetime
from dateutil import relativedelta
from datetime import datetime, date, timedelta
from frappe.model.document import Document
from frappe.utils import getdate, formatdate, today
from frappe import throw, msgprint, _

class ServiceStaffCommissions(Document):
	def validate(self):
		self.set_title()
		self.set_total_count()
		self.calculate_commissions()

	def set_title(self):
		self.title = _('{0} for {1} {2}').format(self.staff_name, self.month, self.year)

	def set_total_count(self):
		self.total_spa_count = 0
		self.total_pt_count = 0
		self.total_pt_count_calculated = 0.0
		self.total_gx_count = 0
		self.total_gx_count_calculated = 0.0
		self.total_sessions = 0.0

		if self.spa_count_table:
			for row in self.spa_count_table:
				self.total_spa_count += 1
		
		if self.fitness_count_table:
			for row in self.fitness_count_table:
				self.total_pt_count += 1
				self.total_pt_count_calculated += float(row.count)

		if self.gc_count_table:
			for row in self.gc_count_table:
				self.total_gx_count += 1
				self.total_gx_count_calculated += float(row.count)
		
		self.total_sessions = self.total_pt_count_calculated + self.total_gx_count_calculated
	
	def calculate_commissions(self):
		self.commission_from_fitness_training = 0.0
		self.commission_from_group_class = 0.0
		self.commission_from_spa = 0.0

		settings = frappe.get_doc('Fitness Training Settings')

		if self.total_spa_count > 0:
			for row in self.spa_count_table:
				row.commission_amount = (row.service_amount * row.commission_percentage)/100
				self.commission_from_spa += row.commission_amount
			
		if self.total_gx_count_calculated > 0:
			self.commission_from_group_class = self.total_gx_count_calculated * settings.group_class_rate

		if self.total_pt_count_calculated > 0:
			scale = {(0, 30): 40, (30, 60): 60, (60, 90): 80, (90, 120): 100, (120, 150): 120, (150, math.inf): 140}
			hours_worked = self.total_sessions

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
			hours_worked_1 = self.total_gx_count_calculated

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
			
			self.commission_from_fitness_training = total_session - total_gc
		
		self.total_commission = self.commission_from_fitness_training + self.commission_from_group_class + self.commission_from_spa

@frappe.whitelist()
def update_spa_commissions():
	appointments_list = frappe.get_all('Spa Appointment', filters={'count_updated': 0, 'appointment_status': ['in', {'Completed', 'No Show'}], 'payment_status': 'Paid'})
	if appointments_list:
		for appointments in appointments_list:
			commission_percentage = 0.0
			appointment = frappe.get_doc('Spa Appointment', appointments.name)
			spa_service = frappe.get_doc('Spa Services', appointment.spa_service)
			staff = frappe.get_doc('Service Staff', appointment.service_staff)
			if staff.spa_service_assignment:
				for row in staff.spa_service_assignment:
					if row.spa_group == spa_service.spa_group:
						commission_percentage = row.commission
			
			if type(appointment.appointment_date)==str:
				dates = datetime.strptime(appointment.appointment_date, "%Y-%m-%d")
			else:
				dates = appointment.appointment_date
			months = dates.month
			years = dates.year
			month_name = ['January','February','March','April','May','June','July','August','September','October','November','December']
			months_name = month_name[int(months) - 1]

			discount_amount = 0.0
			if appointment.membership_status == "Member":
				client = frappe.get_doc('Client', appointment.client_id)
				if client.membership_history:
					for row in client.membership_history:
						if row.status == "Active":
							mem = frappe.get_doc('Memberships', row.membership)
							discount_amount = mem.spa_discount
			
			if spa_service.session_type == "Standard":
				net_total = spa_service.price
			elif spa_service.session_type == "Complimentary":
				net_total = spa_service.regular_price_reference

			total_price = float(net_total) - (float(net_total) * float(discount_amount)/100)	

			comm_list = frappe.get_all('Service Staff Commissions', filters={'staff_name': appointment.service_staff, 'month': months_name, 'year': years})
			if comm_list:
				for comm in comm_list:
					doc = frappe.get_doc('Service Staff Commissions', comm.name)
					doc.append('spa_count_table', {
						'appointment_date': dates,
						'appointment_doc': appointment.name,
						'service_amount': total_price,
						'commission_percentage' : commission_percentage
					})
					doc.save()
			else:
				doc = frappe.get_doc({
					'doctype': 'Service Staff Commissions',
					'staff_name': appointment.service_staff,
					'month': months_name,
					'year': years,
					'spa_count_table': [{
						'appointment_date': dates,
						'appointment_doc': appointment.name,
						'service_amount': total_price,
						'commission_percentage' : commission_percentage
					}]
				})
				doc.save()
			frappe.db.set_value('Spa Appointment', appointment.name, 'count_updated', 1)
			frappe.db.commit()

@frappe.whitelist()
def update_pt_commissions():
	appointments_list = frappe.get_all('Fitness Training Appointment', filters={'count_updated': 0, 'appointment_status': ['in', {'Completed', 'No Show'}], 'payment_status': 'Paid'})
	if appointments_list:
		for appointments in appointments_list:
			appointment = frappe.get_doc('Fitness Training Appointment', appointments.name)
			pt_service = frappe.get_doc('Fitness Services', appointment.fitness_service)
			settings = frappe.get_doc('Fitness Training Settings')

			if type(appointment.appointment_date)==str:
				dates = datetime.strptime(appointment.appointment_date, "%Y-%m-%d")
			else:
				dates = appointment.appointment_date
			months = dates.month
			years = dates.year
			month_name = ['January','February','March','April','May','June','July','August','September','October','November','December']
			months_name = month_name[int(months) - 1]

			if pt_service.session_type == "Standard":
				if pt_service.session_for == "Single":
					count = settings.single_session
				elif pt_service.session_for == "Couple":
					count = settings.couple_session
			elif pt_service.session_type == "Complimentary":
				count = settings.complimentary_session

			comm_list = frappe.get_all('Service Staff Commissions', filters={'staff_name': appointment.service_staff, 'month': months_name, 'year': years})
			if comm_list:
				for comm in comm_list:
					doc = frappe.get_doc('Service Staff Commissions', comm.name)
					doc.append('fitness_count_table', {
						'appointment_date': dates,
						'appointment_doc': appointment.name,
						'client_name': appointment.client_name,
						'service_category' : pt_service.session_for,
						'count': count
					})
					doc.save()
			else:
				doc = frappe.get_doc({
					'doctype': 'Service Staff Commissions',
					'staff_name': appointment.service_staff,
					'month': months_name,
					'year': years,
					'fitness_count_table': [{
						'appointment_date': dates,
						'appointment_doc': appointment.name,
						'client_name': appointment.client_name,
						'service_category' : pt_service.session_for,
						'count': count
					}]
				})
				doc.save()
			frappe.db.set_value('Fitness Training Appointment', appointment.name, 'count_updated', 1)
			frappe.db.commit()

@frappe.whitelist()
def update_gc_commissions():
	gc_list = frappe.get_all('Group Class', filters={'count_updated': 0, 'class_status': 'Completed'})
	if gc_list:
		for gc in gc_list:
			group_class = frappe.get_doc('Group Class', gc.name)
			settings = frappe.get_doc('Fitness Training Settings')

			count = settings.group_class_session

			if type(group_class.class_date)==str:
				dates = datetime.strptime(group_class.class_date, "%Y-%m-%d")
			else:
				dates = group_class.class_date
			months = dates.month
			years = dates.year
			month_name = ['January','February','March','April','May','June','July','August','September','October','November','December']
			months_name = month_name[int(months) - 1]

			comm_list = frappe.get_all('Service Staff Commissions', filters={'staff_name': group_class.trainer_name, 'month': months_name, 'year': years})
			if comm_list:
				for comm in comm_list:
					doc = frappe.get_doc('Service Staff Commissions', comm.name)
					doc.append('gc_count_table', {
						'class_date': dates,
						'appointment_doc': group_class.name,
						'count': count
					})
					doc.save()
			else:
				doc = frappe.get_doc({
					'doctype': 'Service Staff Commissions',
					'staff_name': group_class.trainer_name,
					'month': months_name,
					'year': years,
					'gc_count_table': [{
						'class_date': dates,
						'appointment_doc': group_class.name,
						'count': count
					}]
				})
				doc.save()
			frappe.db.set_value('Group Class', group_class.name, 'count_updated', 1)
			frappe.db.commit()