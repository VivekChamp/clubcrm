# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import getdate, get_time, flt, cint
from frappe.model.naming import getseries
from club_crm.club_crm.doctype.client_sessions.client_sessions import create_sessions
from frappe.model.document import Document

class Memberships(Document):
	# Remove after membership data upload
	# def after_insert(self):
	# 	self.create_client_sessions()

	def before_insert(self):
		self.set_membership_number()

	def after_insert(self):
		self.set_membership_history()

	def validate(self):
		self.set_expiry()
		self.set_title()
		self.set_status()
		self.set_member_number()
		if not self.membership_id:
			self.set_membership_number()

	def on_update(self):
		self.set_membership_history()
	
	def on_trash(self):
		self.delete_membership_application_link()
		self.delete_membership_history()
		self.delete_membership_number()

	# Set expiry date based on the membership plan
	def set_expiry(self):
		if type(self.start_date) == str:
			start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
		else:
			start_date = self.start_date
		expiry_date = start_date + timedelta(seconds=float(self.duration))
		self.actual_expiry_date = expiry_date.strftime("%Y-%m-%d")
		if self.extended == 0:
			self.expiry_date = self.actual_expiry_date

	# Generate and set a membership number based on the membership type
	def set_membership_number(self):
		if self.memberships_type == "New":
			if self.membership_type == "Single Membership":
				self.membership_id = getseries_add("S", 4)
			if self.membership_type == "Couple Membership":
				self.membership_id = getseries_add("C", 4)
			if self.membership_type == "Family Membership":
				self.membership_id = getseries_add("F", 4)
	
	# Set title for the document
	def set_title(self):
		self.title = _('{0} - {1}').format(self.client_name_1, self.membership_id)

	# Set the membership status while saving document
	def set_status(self):
		today = getdate()
		expiry_date = getdate(self.expiry_date)

		# If expiry date is past, set membership status as expired
		if expiry_date < today:
			self.membership_status = 'Expired'
		elif expiry_date >= today and self.membership_status != "Draft" and self.membership_status != "Cancelled":
			self.membership_status = 'Active'

	# Set member number, card number and other details to the respective client document
	def set_member_number(self):
		if self.member_no_1:
			frappe.db.set_value('Client', self.client_id_1, 'member_id', self.member_no_1)
		if self.card_no_1:
			frappe.db.set_value('Client', self.client_id_1, 'card_no', self.card_no_1)
		frappe.db.set_value('Client', self.client_id_1, {
			'primary_member': 1,
			'membership_id': self.membership_id,
			'assigned_to': self.assigned_to_1
		})

		if self.membership_type == "Couple Membership":
			if self.member_no_2:
				frappe.db.set_value('Client', self.client_id_2, 'member_id', self.member_no_2)
			if self.card_no_2:
				frappe.db.set_value('Client', self.client_id_2, 'card_no', self.card_no_2)
			frappe.db.set_value('Client', self.client_id_2, {
				'membership_id': self.membership_id,
				'assigned_to': self.assigned_to_2
			})
		
		if self.membership_type == "Family Membership":
			if self.member_no_2:
				frappe.db.set_value('Client', self.client_id_2, 'member_id', self.member_no_2)
			if self.card_no_2:
				frappe.db.set_value('Client', self.client_id_2, 'card_no', self.card_no_2)
			frappe.db.set_value('Client', self.client_id_2, {
				'membership_id': self.membership_id,
				'assigned_to': self.assigned_to_2
			})
			
			if self.additional_members_item:
				for row in self.additional_members_item:
					if row.member_no:
						frappe.db.set_value('Client', row.client_id, 'member_id', row.member_no)
					if row.card_no:
						frappe.db.set_value('Client', row.client_id, 'card_no', row.card_no)
					frappe.db.set_value('Client', row.client_id, {
						'membership_id': self.membership_id,
						'assigned_to': self.assigned_to
					})

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

	# Set membership details on the client document as membership history
	def set_membership_history(self):
		client_1 = frappe.get_doc('Client', self.client_id_1)

		match = False
		if client_1.membership_history:
			for entry in client_1.membership_history:
				if self.name == entry.membership:
					match = True
					entry.membership_plan = self.membership_plan,
					entry.start_date = self.start_date,
					entry.end_date = self.expiry_date,
					entry.status = self.membership_status
		if not match:
			client_1.append('membership_history', {
			"membership": self.name,
			"membership_plan": self.membership_plan,
			"start_date": self.start_date,
			"end_date": self.expiry_date,
			"status": self.membership_status
			})
		client_1.save()

		if self.membership_type == "Couple Membership":
			client_2 = frappe.get_doc('Client', self.client_id_2)

			match = False
			if client_2.membership_history:
				for entry in client_2.membership_history:
					if self.name == entry.membership:
						match = True
						entry.membership_plan = self.membership_plan,
						entry.start_date = self.start_date,
						entry.end_date = self.expiry_date,
						entry.status = self.membership_status
			if not match:
				client_2.append('membership_history', {
				"membership": self.name,
				"membership_plan": self.membership_plan,
				"start_date": self.start_date,
				"end_date": self.expiry_date,
				"status": self.membership_status
				})
			client_2.save()

		if self.membership_type == "Family Membership":
			client_2 = frappe.get_doc('Client', self.client_id_2)

			match = False
			if client_2.membership_history:
				for entry in client_2.membership_history:
					if self.name == entry.membership:
						match = True
						entry.membership_plan = self.membership_plan,
						entry.start_date = self.start_date,
						entry.end_date = self.expiry_date,
						entry.status = self.membership_status
			if not match:
				client_2.append('membership_history', {
				"membership": self.name,
				"membership_plan": self.membership_plan,
				"start_date": self.start_date,
				"end_date": self.expiry_date,
				"status": self.membership_status
				})
			client_2.save()
			
			for row in self.additional_members_item:
				client = frappe.get_doc('Client', row.client_id)

				match = False
				if client.membership_history:
					for entry in client.membership_history:
						if self.name == entry.membership:
							match = True
							entry.membership_plan = self.membership_plan,
							entry.start_date = self.start_date,
							entry.end_date = self.expiry_date,
							entry.status = self.membership_status
				if not match:
					client.append('membership_history', {
					"membership": self.name,
					"membership_plan": self.membership_plan,
					"start_date": self.start_date,
					"end_date": self.expiry_date,
					"status": self.membership_status
					})
				client.save()

	def delete_membership_application_link(self):
		frappe.db.set_value("Memberships Application", self.membership_application, "membership_document", "", update_modified=False)
		
	def delete_membership_history(self):
		client_1 = frappe.get_doc('Client', self.client_id_1)
		if client_1.membership_history:
			for entry in client_1.membership_history:
				if self.name == entry.membership:
					client_1.remove(entry)
					client_1.save()
		
		if self.membership_type == "Couple Membership":
			client_2 = frappe.get_doc('Client', self.client_id_2)
			if client_2.membership_history:
				for entry in client_2.membership_history:
					if self.name == entry.membership:
						client_2.remove(entry)
						client_2.save()
		
		if self.membership_type == "Family Membership":
			client_2 = frappe.get_doc('Client', self.client_id_2)
			if client_2.membership_history:
				for entry in client_2.membership_history:
					if self.name == entry.membership:
						client_2.remove(entry)
						client_2.save()

			for row in self.additional_members_item:
				client = frappe.get_doc('Client', row.client_id)
				if client.membership_history:
					for entry in client.membership_history:
						if self.name == entry.membership:
							client.remove(entry)
							client.save()
	
	def delete_membership_number(self):
		client_1 = frappe.get_doc('Client', self.client_id_1)
		if not client_1.membership_history:
			frappe.db.set_value('Client', self.client_id_1, {
				'member_id': None,
				'card_no': None,
				'primary_member': 0,
				'membership_id': None,
				'assigned_to': None
			})
		if self.membership_type == "Couple Membership":
			client_2 = frappe.get_doc('Client', self.client_id_2)
			if not client_2.membership_history:
				frappe.db.set_value('Client', self.client_id_2, {
				'member_id': None,
				'card_no': None,
				'primary_member': 0,
				'membership_id': None,
				'assigned_to': None
			})
		if self.membership_type == "Family Membership":
			client_2 = frappe.get_doc('Client', self.client_id_2)
			if not client_2.membership_history:
				frappe.db.set_value('Client', self.client_id_2, {
				'member_id': None,
				'card_no': None,
				'primary_member': 0,
				'membership_id': None,
				'assigned_to': None
			})
			for row in self.additional_members_item:
				client = frappe.get_doc('Client', row.client_id)
				if not client.membership_history:
					frappe.db.set_value('Client', row.client_id, {
					'member_id': None,
					'card_no': None,
					'primary_member': 0,
					'membership_id': None,
					'assigned_to': None
				})

@frappe.whitelist()
def activate_membership(appointment_id):
	mem = frappe.get_doc('Memberships', appointment_id)
	mem.membership_status = "Active"

	frappe.db.set_value('Client', mem.client_id_1, 'membership_status', 'Member')
	if mem.membership_type == "Couple Membership":
		frappe.db.set_value('Client', mem.client_id_2, 'membership_status', 'Member')
	if mem.membership_type == "Family Membership":
		for row in mem.additional_members_item:
			frappe.db.set_value('Client', row.client_id, 'membership_status', 'Member')
	mem.save()

@frappe.whitelist()
def cancel_membership(appointment_id):
	mem = frappe.get_doc('Memberships', appointment_id)
	mem.membership_status = "Cancelled"
	mem.save()

@frappe.whitelist()
def update_membership_status():
	# update the status of membership daily
	today = getdate()
	memberships = frappe.get_all('Memberships', filters={'membership_status': 'Active'})

	for membership in memberships:
		mem = frappe.get_doc('Memberships', membership.name)
		expiry_date = getdate(mem.expiry_date)
		# If expiry date is past, set membership status as expired
		if expiry_date < today:
			frappe.db.set_value('Memberships', membership.name, 'membership_status', 'Expired')
			frappe.db.commit()

def getseries_add(key, digits):
	# series created ?
	current = frappe.db.sql("SELECT `current` FROM `tabSeries` WHERE `name`=%s FOR UPDATE", (key,))
	if current and current[0][0] is not None:
		current = current[0][0]
		# yes, update it
		frappe.db.sql("UPDATE `tabSeries` SET `current` = `current` + 1 WHERE `name`=%s", (key,))
		frappe.db.commit()
		current = cint(current) + 1
	else:
		# no, create it
		frappe.db.sql("INSERT INTO `tabSeries` (`name`, `current`) VALUES (%s, 1)", (key,))
		frappe.db.commit()
		current = 1
	return (key+('%0'+str(digits)+'d') % current)

def getseries_delete(key, digits):
	# series created ?
	current = frappe.db.sql("SELECT `current` FROM `tabSeries` WHERE `name`=%s FOR UPDATE", (key,))
	if current and current[0][0] is not None:
		current = current[0][0]
		# yes, update it
		frappe.db.sql("UPDATE `tabSeries` SET `current` = `current` - 1 WHERE `name`=%s", (key,))
		frappe.db.commit()
	else:
		# no, create it
		frappe.db.sql("INSERT INTO `tabSeries` (`name`, `current`) VALUES (%s, 0)", (key,))
		frappe.db.commit()