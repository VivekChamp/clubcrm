# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from datetime import datetime


class SpaProgressNotes(Document):
	pass
	# def validate(self):
	# 	self.check_progressnotes()
	# def on_submit(self):
	# 	if self.appointment_id:
	# 		frappe.db.set_value('Spa Appointment', self.appointment_id, 'status', 'Complete')
	# 		doc= frappe.get_doc('Spa Appointment', self.appointment_id)
	# 		doc.reload()
	
	# def on_cancel(self):
	# 	if self.appointment_id:
	# 		frappe.db.set_value('Spa Appointment', self.appointment_id, 'status', 'Open')
	# 		doc= frappe.get_doc('Spa Appointment', self.appointment_id)
	# 		doc.reload()

	# def check_progressnotes(self):
	# 	progressnote_check = frappe.get_all('Spa Progress Notes', filters={'appointment_id':self.appointment_id})
	# 	if progressnote_check:
	# 		frappe.throw("Progress Notes already exist for this appointment. If you wish to add more notes, please click on the progress notes linked to this appointment from the dashboard.")

@frappe.whitelist()
def progress_notes(appointment_id,notes):
	progress = frappe.get_doc({
				"doctype": 'Spa Progress Notes',
				"appointment_id": appointment_id,
				"notes": notes
				})
	progress.insert()
	progress.submit()

# @frappe.whitelist()
# def create_progress_notes(source_name, target_doc=None):
# 	def set_missing_values(source, target):
# 		target.appointment_id = source_name
# 		target.time = datetime.now()

# 	doc = get_mapped_doc('Spa Appointment', source_name, {
# 			'Spa Appointment': {
# 				'doctype': 'Spa Progress Notes',
# 				'field_map': [
# 					['client_id', 'client_id'],
# 					['client_name', 'client_name'],
# 					['spa_item', 'spa_item'],
# 					['spa_therapist', 'spa_therapist'],
# 					['spa_duration', 'total_duration'],
# 					['spa_room', 'club_room']
# 				]
# 			}
# 		}, target_doc, set_missing_values)
# 	return doc

@frappe.whitelist()
def check_if_exists(appointment_id):
	progress_notes = frappe.get_all('Spa Progress Notes', filters={'appointment_id':appointment_id})
	if progress_notes:
		return 1
	else:
		return 0