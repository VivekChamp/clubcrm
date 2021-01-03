# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class SpaProgressNotes(Document):
	def on_update(self):
		if self.appointment_id:
			frappe.db.set_value('Spa Appointment', self.appointment_id, 'status', 'Complete')
	
	def on_cancel(self):
		if self.appointment_id:
			frappe.db.set_value('Spa Appointment', self.appointment_id, 'status', 'Complete')

@frappe.whitelist()
def create_progress_notes(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.appointment_id = source_name

	doc = get_mapped_doc('Spa Appointment', source_name, {
			'Spa Appointment': {
				'doctype': 'Spa Progress Notes',
				'field_map': [
					['client_id', 'client_id'],
					['client_name', 'client_name'],
					['spa_item', 'spa_item'],
					['spa_therapist', 'spa_therapist'],
					['spa_duration', 'total_duration'],
					['spa_room', 'club_room']
				]
			}
		}, target_doc, set_missing_values)
	return doc