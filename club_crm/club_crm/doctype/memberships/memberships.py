# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import getdate, get_time, flt
from club_crm.club_crm.doctype.client_sessions.client_sessions import create_sessions
from frappe.model.document import Document

class Memberships(Document):
	# Remove after membership data upload
	# def after_insert(self):
	# 	self.create_client_sessions()

	def validate(self):
		self.set_expiry()
		self.set_membership_number()
		self.set_title()
		self.set_status()
		self.set_member_number()

	def set_expiry(self):
		if type(self.start_date) == str:
			start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
		else:
			start_date = self.start_date
		expiry_date = start_date + timedelta(seconds=float(self.duration))
		self.actual_expiry_date = expiry_date.strftime("%Y-%m-%d")
		if self.extended == 0:
			self.expiry_date = self.actual_expiry_date
	
	def set_membership_number(self):
		if not self.membership_id:
			mem = frappe.db.count('Memberships')
			if mem !=0:
				mem = frappe.get_last_doc('Memberships')
				self.membership_id = mem.membership_id + 1
			else:
				self.membership_id = 100000

	def set_title(self):
		self.title = _('{0} - {1}').format(self.client_name_1,self.membership_id)

	def set_status(self):
		today = getdate()
		expiry_date = getdate(self.expiry_date)

		# If expiry date is past, set membership status as expired
		if expiry_date < today:
			self.membership_status = 'Expired'
		elif expiry_date >= today and self.membership_status != "Draft":
			self.membership_status = 'Active'

	def set_member_number(self):
		frappe.db.set_value('Client', self.client_id_1, 'member_id', self.member_no_1)
		frappe.db.set_value('Client', self.client_id_1, 'card_no', self.card_no_1)
		frappe.db.set_value('Client', self.client_id_1, 'primary_member', 1)
		frappe.db.set_value('Client', self.client_id_1, 'membership_id', self.membership_id)

		if self.membership_type == "Couple Membership":
			frappe.db.set_value('Client', self.client_id_2, 'member_id', self.member_no_2)
			frappe.db.set_value('Client', self.client_id_2, 'card_no', self.card_no_2)
			frappe.db.set_value('Client', self.client_id_2, 'membership_id', self.membership_id)
		
		if self.membership_type == "Family Membership":
			for row in self.additional_members_item:
				frappe.db.set_value('Client', row.client_id, 'member_id', row.member_no)
				frappe.db.set_value('Client', row.client_id, 'card_no', row.card_no)
				frappe.db.set_value('Client', row.client_id, 'membership_id', self.membership_id)

	# Remove after membership data upload
	def create_client_sessions(self):
		if type(self.start_date) == str:
			start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
		else:
			start_date = self.start_date
		return start_date

		mem_plan = frappe.get_doc('Memberships Plan', self.membership_plan)
		club_package = frappe.get_doc('Club Packages', mem_plan.benefits_item)
		today = getdate()
		if club_package.package_table:
			for item in club_package.package_table:
				create_sessions(self.client_id_1,mem_plan.benefits_item,start_date,item.service_type,item.service_name,item.no_of_sessions,item.validity)
				if self.membership_type == "Couple Membership":
					create_sessions(self.client_id_2,mem_plan.benefits_item,start_date,item.service_type,item.service_name,item.no_of_sessions,item.validity)
				if self.membership_type == "Family Membership":
					create_sessions(self.client_id_2,mem_plan.benefits_item,start_date,item.service_type,item.service_name,item.no_of_sessions,item.validity)
					for row in self.additional_members_item:
						if type(row.birth_date) == str:
							dob = datetime.strptime(row.birth_date, "%Y-%m-%d")
						else:
							dob = row.birth_date
						age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
						if age >= 18:
							create_sessions(row.client_id,mem_plan.benefits_item,start_date,item.service_type,item.service_name,item.no_of_sessions,item.validity)
		
@frappe.whitelist()
def activate_membership(appointment_id):
	frappe.db.set_value('Memberships', appointment_id, 'membership_status', 'Active')
	mem = frappe.get_doc('Memberships', appointment_id)

	frappe.db.set_value('Client', mem.client_id_1, 'membership_status', 'Member')
	if mem.membership_type == "Couple Membership":
		frappe.db.set_value('Client', mem.client_id_2, 'membership_status', 'Member')
	if mem.membership_type == "Family Membership":
		for row in mem.additional_members_item:
			frappe.db.set_value('Client', row.client_id, 'membership_status', 'Member')

@frappe.whitelist()
def update_membership_status():
	# update the status of membership daily
	memberships = frappe.get_all('Memberships', filters={'membership_status': 'Active'})

	for membership in memberships:
		frappe.get_doc('Memberships', membership.name).set_status()
