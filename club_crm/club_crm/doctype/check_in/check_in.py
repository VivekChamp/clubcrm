# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
from frappe.model.mapper import get_mapped_doc

class CheckIn(Document):

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

	def on_trash(self):
		self.delete_checkin_link()

	def delete_checkin_link(self):
		if self.check_in_type == "Spa":
			if self.spa_booking:
				frappe.db.set_value("Spa Appointment", self.spa_booking, "checkin_document", "", update_modified=False)

@frappe.whitelist()
def club_checkin(client_id):
	user = frappe.get_doc('User',frappe.session.user)
	doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id,
		'checked_in_by': user.full_name
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
	user = frappe.get_doc('User',frappe.session.user)
	doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id,
		'check_in_type' : 'Spa',
		'naming_series' : 'CHK-.YYYY.-SPA.-',
		'spa_booking': appointment_id,
		'checked_in_by': user.full_name
        })
	doc.insert()
	doc.submit()
	
	frappe.db.set_value("Spa Appointment", appointment_id, "appointment_status", "Checked-in")
	frappe.db.set_value("Spa Appointment", appointment_id, "checkin_document", doc.name)

	frappe.msgprint(msg='Checked-in successfully', title='Success')

@frappe.whitelist()
def fitness_checkin(client_id, appointment_id):
	user = frappe.get_doc('User',frappe.session.user)
	doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id,
		'check_in_type' : 'Fitness',
		'naming_series' : 'CHK-.YYYY.-FITNESS.-',
		'fitness_booking': appointment_id,
		'checked_in_by': user.full_name
        })
	doc.insert()
	doc.submit()
	
	frappe.db.set_value("Fitness Training Appointment", appointment_id, "appointment_status", "Checked-in")
	frappe.db.set_value("Fitness Training Appointment", appointment_id, "checkin_document", doc.name)

	frappe.msgprint(msg='Checked-in successfully', title='Success')

@frappe.whitelist()
def gc_checkin(client_id, doc_id):
	user = frappe.get_doc('User',frappe.session.user)
	doc = frappe.get_doc({
        'doctype': 'Check In',
        'client_id': client_id,
		'check_in_type' : 'Group Class',
		'naming_series' : 'CHK-.YYYY.-GC.-',
		'class_attendee_id': doc_id,
		'checked_in_by': user.full_name
        })
	doc.insert()
	doc.submit()
	
	frappe.db.set_value("Group Class Attendees", doc_id, "attendee_status", "Checked-in")
	frappe.db.set_value("Group Class Attendees", doc_id, "checkin_document", doc.name)

	frappe.msgprint(msg='Checked-in successfully', title='Success')