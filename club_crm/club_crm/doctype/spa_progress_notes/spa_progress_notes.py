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

@frappe.whitelist()
def progress_notes(appointment_id,notes):
	progress = frappe.get_doc({
				"doctype": 'Spa Progress Notes',
				"appointment_id": appointment_id,
				"notes": notes
				})
	progress.insert()
	progress.submit()
	frappe.db.set_value("Spa Appointment", appointment_id, "progress_notes_id", progress.name)

@frappe.whitelist()
def check_if_exists(appointment_id):
	progress_notes = frappe.get_all('Spa Progress Notes', filters={'appointment_id':appointment_id})
	if progress_notes:
		return 1
	else:
		return 0