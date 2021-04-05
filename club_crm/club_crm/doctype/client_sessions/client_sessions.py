# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date, time
from frappe.model.document import Document

class ClientSessions(Document):
	def validate(self):
		self.set_expiry_date()
		self.set_title()
		# self.set_session_count()
		self.set_remaining_sessions()
		self.set_status()
		# self.check_spa_bookings()
		# self.check_fitness_bookings()	

	def set_expiry_date(self):
		if self.start_date:
			if type(self.start_date) == str:
				start_datetime = datetime.strptime(self.start_date, "%Y-%m-%d")
			else:
				start_datetime = self.start_date
			if self.extension:
				expiry_date = start_datetime + timedelta(seconds=float(self.validity)) + timedelta(seconds=float(self.extension))
			else:
				expiry_date = start_datetime + timedelta(seconds=float(self.validity))
			self.expiry_date = datetime.strftime(expiry_date, "%Y-%m-%d")
		else:
			frappe.throw("Please set the start date")

	def set_title(self):
		self.title = _('{0}').format(self.service_name)

	def set_session_count(self):
		if self.service_type == "Spa Services":
			booked_sessions = frappe.get_all('Spa Appointment', filters={'session_name': self.name,'appointment_status':['in',{'Scheduled', 'Open'}]})
			if booked_sessions:
				booked = len(booked_sessions)
				self.booked_sessions = booked
			else:
				booked = 0
				self.booked_sessions = 0

			used_sessions = frappe.get_all('Spa Appointment', filters={'session_name': self.name,'appointment_status': ['in',{'Complete', 'No Show'}]})
			if used_sessions:
				used = len(used_sessions)
				self.used_sessions = used
			else:
				used = 0
				self.used_sessions = 0

		if self.service_type == "Fitness Services":
			booked_sessions = frappe.get_all('Fitness Training Appointment', filters={'session_name': self.name,'appointment_status':['in',{'Scheduled', 'Open'}]})
			if booked_sessions:
				booked = len(booked_sessions)
				self.booked_sessions = booked
			else:
				booked = 0
				self.booked_sessions = 0

			used_sessions = frappe.get_all('Fitness Training Appointment', filters={'session_name': self.name,'appointment_status': ['in',{'Complete', 'No Show'}]})
			if used_sessions:
				used = len(used_sessions)
				self.used_sessions = used
			else:
				used = 0
				self.used_sessions = 0

	def set_remaining_sessions(self):
		self.remaining_sessions = self.total_sessions - self.used_sessions
		self.remaining_session_text = _('{0}/{1}').format(self.remaining_sessions,self.total_sessions)

	def set_status(self):
		today = getdate()
		if type(self.expiry_date) == str:
			expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
		else:
			expiry = self.expiry_date

		# If expiry date is less than today, change the status to expired.
		expiry_date = expiry.date()

		if not self.session_status:
			if expiry_date < today:
				self.session_status = 'Expired'
			if expiry_date >= today:
				self.session_status = 'Active'

		if self.session_status=="Active" or self.session_status=="On Hold":
			if expiry_date < today:
				self.session_status = 'Expired'
		if self.session_status=="Expired":
			if expiry_date >= today:
				self.session_status = 'Active'
		if self.remaining_sessions == 0:
			self.session_status = 'Complete'

@frappe.whitelist()
def create_session(client_id, package_name, service_type, service_name, no_of_sessions, validity):
	doc= frappe.get_doc({
		"doctype": 'Client Sessions',
		"client_id": client_id,
		"package_name": package_name,
		"service_type": service_type,
		"service_name": service_name,
		"total_sessions": no_of_sessions,
		"validity": validity
	})
	doc.save()

# @frappe.whitelist()
# def create_sessions(client_id,package_name,start_date,service_type,service_name,no_of_sessions,validity):
# 	if type(start_date) == str:
# 		new_start_date = datetime.strptime(start_date, "%Y-%m-%d")
# 	else:
# 		new_start_date = start_date
# 	doc= frappe.get_doc({
# 		"doctype": 'Client Sessions',
# 		"client_id": client_id,
# 		"package_name": package_name,
# 		"start_date" : new_start_date,
# 		"service_type": service_type,
# 		"service_name": service_name,
# 		"total_sessions": no_of_sessions,
# 		"validity": validity
# 	})
# 	doc.save()

@frappe.whitelist()
def create_sessions(doc, method=None):
	if type(doc.start_date) == str:
		new_start_date = datetime.strptime(doc.start_date, "%Y-%m-%d")
	else:
		new_start_date = doc.start_date

	mem_plan = frappe.get_doc('Memberships Plan', doc.membership_plan)
	club_package = frappe.get_doc('Club Packages', mem_plan.benefits_item)

	today = getdate()
	if club_package.package_table:
		for item in club_package.package_table:
			cs_1 = frappe.get_doc({
				"doctype": 'Client Sessions',
				"client_id": doc.client_id_1,
				"package_name": mem_plan.benefits_item,
				"start_date" : new_start_date,
				"service_type": item.service_type,
				"service_name": item.service_name,
				"total_sessions": item.no_of_sessions,
				"validity": item.validity
			})
			cs_1.save()

			if doc.membership_type == "Couple Membership":
				cs_2 = frappe.get_doc({
					"doctype": 'Client Sessions',
					"client_id": doc.client_id_2,
					"package_name": mem_plan.benefits_item,
					"start_date" : new_start_date,
					"service_type": item.service_type,
					"service_name": item.service_name,
					"total_sessions": item.no_of_sessions,
					"validity": item.validity
				})
				cs_2.save()

			if doc.membership_type == "Family Membership":
				cs_2 = frappe.get_doc({
					"doctype": 'Client Sessions',
					"client_id": doc.client_id_2,
					"package_name": mem_plan.benefits_item,
					"start_date" : new_start_date,
					"service_type": item.service_type,
					"service_name": item.service_name,
					"total_sessions": item.no_of_sessions,
					"validity": item.validity
				})
				cs_2.save()

				for row in doc.additional_members_item:
					if type(row.birth_date) == str:
						dob = datetime.strptime(row.birth_date, "%Y-%m-%d")
					else:
						dob = row.birth_date
					age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
					if age >= 18:
						cs = frappe.get_doc({
							"doctype": 'Client Sessions',
							"client_id": row.client_id,
							"package_name": mem_plan.benefits_item,
							"start_date" : new_start_date,
							"service_type": item.service_type,
							"service_name": item.service_name,
							"total_sessions": item.no_of_sessions,
							"validity": item.validity
						})
						cs.save()

@frappe.whitelist()
def check_spa_bookings(session_name):
	client_session = frappe.get_doc('Client Sessions', session_name)
	client_session.save()
	# booked_sessions = frappe.get_all('Spa Appointment', filters={'session_name': session_name,'appointment_status':['in',{'Scheduled', 'Open'}]})
	# if booked_sessions:
	# 	booked = len(booked_sessions)
	# 	frappe.db.set_value('Client Sessions', session_name, 'booked_sessions', booked)
	# else:
	# 	booked = 0
	# 	frappe.db.set_value('Client Sessions', session_name, 'booked_sessions', 0)
	# used_sessions = frappe.get_all('Spa Appointment', filters={'session_name': session_name,'appointment_status': ['in',{'Complete', 'No Show'}]})
	# if used_sessions:
	# 	used = len(used_sessions)
	# 	frappe.db.set_value('Client Sessions', session_name, 'used_sessions', used)
	# else:
	# 	used = 0
	# 	frappe.db.set_value('Client Sessions', session_name, 'used_sessions', 0)
	# frappe.db.commit()
	# # client_session.save()

@frappe.whitelist()
def check_fitness_bookings(session_name):
	client_session = frappe.get_doc('Client Sessions', session_name)
	booked_sessions = frappe.get_all('Fitness Training Appointment', filters={'session_name': session_name,'appointment_status':['in',{'Scheduled', 'Open'}]})
	if booked_sessions:
		booked = len(booked_sessions)
		frappe.db.set_value('Client Sessions', session_name, 'booked_sessions', booked)
	else:
		booked = 0
		frappe.db.set_value('Client Sessions', session_name, 'booked_sessions', 0)
	used_sessions = frappe.get_all('Fitness Training Appointment', filters={'session_name': session_name,'appointment_status': ['in',{'Complete', 'No Show'}]})
	if used_sessions:
		used = len(used_sessions)
		frappe.db.set_value('Client Sessions', session_name, 'used_sessions', used)
	else:
		used = 0
		frappe.db.set_value('Client Sessions', session_name, 'used_sessions', 0)
	frappe.db.commit()
	# client_session.save()