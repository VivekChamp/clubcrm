# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class CheckIn(Document):
	def on_submit(self):
		if self.check_in_type=="Group Class":
			frappe.db.set_value('Group Class Attendees', self.class_attendee_id,'checked_in', 'Yes')

	def validate(self):
		self.check_spa()

	def check_spa(self):
		spa_check = frappe.get_all('Check In', filters={'docstatus':1,'spa_booking': self.spa_booking})
		if spa_check:
			frappe.throw("Already Checked in")

@frappe.whitelist()
def spa_checkin(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.series = "CHK-.YYYY.-SPA.-"
		target.check_in_type = "Spa"
		target.spa_booking = source_name

	doc = get_mapped_doc('Spa Appointment', source_name, {
			'Spa Appointment': {
				'doctype': 'Check In',
				'field_map': [
					['client_id', 'client_id']
				]
			}
		}, target_doc, set_missing_values)

	return doc