# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
from frappe.model.mapper import get_mapped_doc

class CheckIn(Document):
	def on_submit(self):
		if self.check_in_type=="Group Class":
			frappe.db.set_value('Group Class Attendees', self.class_attendee_id,'checked_in', 'Yes')

	def validate(self):
		self.check_spa()
		self.check_gc()

	def check_spa(self):
		spa_check = frappe.get_all('Check In', filters={'docstatus':1,'spa_booking': self.spa_booking})
		if spa_check:
			frappe.throw("Already Checked in")
	
	def check_gc(self):
		gc_check = frappe.get_all('Check In', filters={'docstatus':1,'class_attendee_id': self.class_attendee_id, 'group_class_id': self.group_class_id})
		if gc_check:
			frappe.throw("Already Checked in")

# @frappe.whitelist()
# def spa_checkin(source_name, target_doc=None):
# 	def set_missing_values(source, target):
# 		target.series = "CHK-.YYYY.-SPA.-"
# 		target.check_in_type = "Spa"
# 		target.spa_booking = source_name

# 	doc = get_mapped_doc('Spa Appointment', source_name, {
# 			'Spa Appointment': {
# 				'doctype': 'Check In',
# 				'field_map': [
# 					['client_id', 'client_id']
# 				]
# 			}
# 		}, target_doc, set_missing_values)

# 	return doc

@frappe.whitelist()
def gc_checkin(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.series = "CHK-.YYYY.-GC.-"
		target.check_in_type = "Group Class"
		target.class_attendee_id = source_name

	doc = get_mapped_doc('Group Class Attendees', source_name, {
			'Group Class Attendees': {
				'doctype': 'Check In',
				'field_map': [
					['client_id', 'client_id']
				]
			}
		}, target_doc, set_missing_values)
	doc.submit()


@frappe.whitelist()
def club_checkin(client_id):
	doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id
        })
	doc.insert()
	doc.submit()

	client = frappe.get_doc('Client', client_id)
	client.status = "Checked-in"
	client.checkin_document = doc.name
	client.save()

@frappe.whitelist()
def club_checkout(client_id):
	client = frappe.get_doc('Client', client_id)
	checkin= frappe.get_doc('Check In', client.checkin_document)
	checkin.check_out_time = now_datetime()
	checkin.save()

	client.status = "Active"
	client.save()

@frappe.whitelist()
def spa_checkin(client_id, appointment_id):
	client = frappe.get_doc('Client', client_id)
	# if client.status != "Checked-in":
	# 	frappe.throw("The client has not checked into the club")
	# else:
	doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id,
		'check_in_type' : 'Spa',
		'naming_series' : 'CHK-.YYYY.-SPA.-',
		'spa_booking': appointment_id
        })
	doc.insert()
	doc.submit()
	
	frappe.db.set_value("Spa Appointment",appointment_id,"appointment_status","Checked-in")

	
# @frappe.whitelist()
# def club_checkin(source_name, target_doc=None):
# 	doc = get_mapped_doc('Client', source_name, {
# 			'Client': {
# 				'doctype': 'Check In',
# 				'field_map': [
# 					['client_id', 'client_id']
# 				]
# 			}
# 		}, target_doc)
# 	doc.submit()

# 	client= frappe.get_doc('Client', doc.client_id)
# 	client.status = "Checked-in"
# 	client.checkin_document = doc.name
# 	client.save()
# 	client.reload()