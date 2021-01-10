# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class FitnessTrainingAppointment(Document):
	pass


@frappe.whitelist()
def book_appointment(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.fitness_session = source_name
		target.time = datetime.now()

	doc = get_mapped_doc('Fitness Training Session', source_name, {
			'Fitness Training Session': {
				'doctype': 'Fitness Training Appointment',
				'field_map': [
					['client_id', 'client_id'],
					['trainer_name', 'trainer_id']
				]
			}
		}, target_doc, set_missing_values)
	return doc