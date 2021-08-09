# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date, time
from club_crm.club_crm.utils.date import add_month
from frappe.model.document import Document

class ClientSessions(Document):
	def validate(self):
		self.set_expiry_date()
		self.set_title()
		self.set_remaining_sessions()
		self.set_status()

	def set_expiry_date(self):
		self.extension = 0.0
		self.no_of_extensions = 0

		if self.session_extension:
			for row in self.session_extension:
				self.no_of_extensions += 1
				self.extension += row.days

		if self.start_date:
			if type(self.start_date) == str:
				start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
			else:
				start_date = self.start_date
			
			if self.package_name:
				if not self.package_name == "Additional Benefits": 
					club_package = frappe.get_doc('Club Packages', self.package_name)
					if club_package.package_table:
						for row in club_package.package_table:
							if self.service_name == row.service_name:
								if row.validity_in == "Months":
									expiry_date = add_month(start_date, row.validity_months)
								elif row.validity_in == "Days":
									expiry_date = start_date + timedelta(seconds=float(row.validity)) - timedelta(seconds=float(86400))

								new_expiry_date = expiry_date + timedelta(seconds=float(self.extension))
								self.actual_expiry_date = expiry_date.strftime("%Y-%m-%d")
								self.expiry_date = new_expiry_date.strftime("%Y-%m-%d")
				else:
					mem = frappe.get_doc('Memberships', self.membership_no)
					mem_plan = frappe.get_doc('Memberships Plan', mem.membership_plan)

					if mem_plan.membership_duration=="Months":
						expiry_date = add_month(start_date, mem_plan.duration_months)
					elif mem_plan.membership_duration=="Days":
						expiry_date = start_date + timedelta(seconds=float(self.duration)) - timedelta(seconds=float(86400))
					
					new_expiry_date = expiry_date + timedelta(seconds=float(self.extension))
					self.actual_expiry_date = expiry_date.strftime("%Y-%m-%d")
					self.expiry_date = new_expiry_date.strftime("%Y-%m-%d")

		else:
			frappe.throw("Please set the start date")

	def set_title(self):
		self.title = _('{0}').format(self.service_name)

	def set_remaining_sessions(self):
		self.remaining_sessions = int(self.total_sessions) - int(self.used_sessions)
		self.remaining_session_text = _('{0}/{1}').format(self.remaining_sessions,self.total_sessions)

	def set_status(self):
		today = date.today()
		if type(self.expiry_date) == str:
			expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d")
		else:
			expiry = self.expiry_date

		# If expiry date is less than today, change the status to expired.
		expiry_date = getdate(expiry)

		if not self.session_status:
			if expiry_date < today:
				self.session_status = 'Expired'
			if expiry_date >= today:
				self.session_status = 'Active'
		
		if self.session_status=="Active":
			if expiry_date < today:
				self.session_status = 'Expired'
			else:
				if self.remaining_sessions == 0:
					self.session_status = 'Complete'

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
	return doc

@frappe.whitelist()
def create_benefit_sessions(client_id,package_name,start_date,service_type,service_name,no_of_sessions,validity,mem_no):
	if type(start_date) == str:
		new_start_date = datetime.strptime(start_date, "%Y-%m-%d")
	else:
		new_start_date = start_date
	doc= frappe.get_doc({
		"doctype": 'Client Sessions',
		"client_id": client_id,
		"package_name": package_name,
		"package_type": "Club",
		"start_date" : new_start_date,
		"service_type": service_type,
		"service_name": service_name,
		"total_sessions": no_of_sessions,
		"validity": validity,
		"membership_no": mem_no,
		"session_status": "Draft",
		"is_benefit": 1
	})
	doc.save()

@frappe.whitelist()
def create_additional_benefit_sessions(client_id,start_date,service_type,service_name,no_of_sessions,validity,mem_no):
	if type(start_date) == str:
		start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
		new_start_date = start_date_dt.date()
	else:
		new_start_date = start_date

	doc= frappe.get_doc({
		"doctype": 'Client Sessions',
		"client_id": client_id,
		"package_name": "Additional Benefits",
		"package_type": "Club",
		"start_date" : new_start_date,
		"service_type": service_type,
		"service_name": service_name,
		"total_sessions": no_of_sessions,
		"validity": validity,
		"membership_no": mem_no,
		"is_benefit": 1,
		"session_status": "Active"
	})
	doc.save()

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
def update_session_status():
	# update the status of sessions daily
	today = getdate()
	session_list = frappe.get_all('Client Sessions', filters={'session_status': 'Active'})
	if session_list:
		for session in session_list:
			client_session = frappe.get_doc('Client Sessions', session.name)
			if type(client_session.expiry_date) == str:
				expiry_date= datetime.strptime(client_session.expiry_date, "%Y-%m-%d")
			else:
				expiry_date = client_session.expiry_date

			# If session is past today's date, set as Expired
			if expiry_date < today:
				frappe.db.set_value("Client Sessions", client_session.name, "session_status", "Expired")
				frappe.db.commit()

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_fitness_session_name(doctype, txt, searchfield, start, page_len, filters):
	sessions = []
	client_sessions = frappe.get_all("Client Sessions", filters={'client_id': filters['client_id'], 'session_status': 'Active', 'service_type': 'Fitness Services'}, fields=['name', 'package_name', 'service_name', 'remaining_sessions', 'booked_sessions' ])
	if client_sessions:
		for session in client_sessions:
			if (session.remaining_sessions - session.booked_sessions) > 0:
				sessions.append([
					session.name, session.package_name, session.service_name
				])
	
	shared_sessions = frappe.get_all("Client Session Sharing", filters={'client_id': filters['client_id']}, fields=['name', 'parent'])
	if shared_sessions:
		for ss in shared_sessions:
			session = frappe.get_doc('Client Sessions', ss.parent)
			if session.session_status == 'Active' and session.service_type == 'Fitness Services':
				if (session.remaining_sessions - session.booked_sessions) > 0:
					sessions.append([
						session.name, session.package_name, session.service_name
					])

	return sessions

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_spa_session_name(doctype, txt, searchfield, start, page_len, filters):
	sessions = []
	client_sessions = frappe.get_all("Client Sessions", filters={'client_id': filters['client_id'], 'session_status': 'Active', 'service_type': 'Spa Services'}, fields=['name', 'package_name', 'service_name', 'remaining_sessions', 'booked_sessions' ])
	if client_sessions:
		for session in client_sessions:
			if (session.remaining_sessions - session.booked_sessions) > 0:
				sessions.append([
					session.name, session.package_name, session.service_name
				])
	
	shared_sessions = frappe.get_all("Client Session Sharing", filters={'client_id': filters['client_id']}, fields=['name', 'parent'])
	if shared_sessions:
		for ss in shared_sessions:
			session = frappe.get_doc('Client Sessions', ss.parent)
			if session.session_status == 'Active' and session.service_type == 'Fitness Services':
				if (session.remaining_sessions - session.booked_sessions) > 0:
					sessions.append([
						session.name, session.package_name, session.service_name
					])

	return sessions