# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
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

	def set_title(self):
		self.title = _('{0} for {1} {2}').format(self.staff_name, self.month, self.year)

	def set_total_count(self):
		self.total_spa_count = 0
		self.total_spa_appointments_calculated = 0
		self.total_pt_count = 0
		self.total_pt_count_calculated = 0
		self.total_gx_count = 0
		self.total_gx_count_calculated = 0

		if self.spa_count_table:
			for row in self.spa_count_table:
				self.total_spa_count += 1
		
		if self.fitness_count_table:
			for row in self.fitness_count_table:
				self.total_pt_count += 1
				self.total_pt_count_calculated += int(row.count)

		if self.gc_count_table:
			for row in self.fitness_count_table:
				self.total_gx_count += 1
				self.total_gx_count_calculated += int(row.count)

@frappe.whitelist()
def add_spa_commission(date, service_staff, doc_id):
	commission_percentage = 0.0
	if type(date)==str:
		dates = datetime.strptime(date, "%Y-%m-%d")
	else:
		dates = date
	months = dates.month
	years = dates.year
	month_name = ['January','February','March','April','May','June','July','August','September','October','November','December']
	months_name = month_name[int(months) - 1]

	spa = frappe.get_doc('Spa Appointment', doc_id)
	staff = frappe.get_doc('Service Staff', service_staff)
	if staff.spa_service_assignment:
		for row in staff.spa_service_assignment:
			if row.spa_group == spa.spa_group:
				commission_percentage = row.commission

	comm_list = frappe.get_all('Service Staff Commissions', filters={'staff_name': service_staff, 'month': months_name, 'year': years})
	if comm_list:
		for comm in comm_list:
			doc = frappe.get_doc('Service Staff Commissions', comm.name)
			doc.append('spa_count_table', {
				'appointment_doc': doc_id,
				'service_amount' : spa.grand_total,
				'commission_percentage': commission_percentage
			})
			doc.save()
	else:
		doc = frappe.get_doc({
			'doctype': 'Service Staff Commissions',
			'staff_name': service_staff,
			'month': months_name,
			'year': years,
			'spa_count_table': [{
				'appointment_doc': doc_id,
				'service_amount' : spa.grand_total,
				'commission_percentage': commission_percentage
			}]
		})
		doc.save()

@frappe.whitelist()
def add_pt_commission(date, service_staff, doc_id):
	count = 0
	if type(date)==str:
		dates = datetime.strptime(date, "%Y-%m-%d")
	else:
		dates = date
	months = dates.month
	years = dates.year
	month_name = ['January','February','March','April','May','June','July','August','September','October','November','December']
	months_name = month_name[int(months) - 1]

	pt = frappe.get_doc('Fitness Training Appointment', doc_id)
	pt_service = frappe.get_doc('Fitness Services', pt.fitness_service)
	if pt_service.session_type != "Complimentary":
		count = 1

	comm_list = frappe.get_all('Service Staff Commissions', filters={'staff_name': service_staff, 'month': months_name, 'year': years})
	if comm_list:
		for comm in comm_list:
			doc = frappe.get_doc('Service Staff Commissions', comm.name)
			doc.append('fitness_count_table', {
				'appointment_doc': doc_id,
				'service_category' : pt_service.session_type,
				'count': count
			})
			doc.save()
	else:
		doc = frappe.get_doc({
			'doctype': 'Service Staff Commissions',
			'staff_name': service_staff,
			'month': months_name,
			'year': years,
			'fitness_count_table': [{
				'appointment_doc': doc_id,
				'service_category' : pt_service.session_type,
				'count': count
			}]
		})
		doc.save()