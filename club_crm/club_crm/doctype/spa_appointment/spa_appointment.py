# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta
from frappe.model.document import Document
from club_crm.api.wallet import get_balance

class SpaAppointment(Document):
	def after_insert(self):
			self.calculate_time()
			self.check_discount()

	def before_submit(self):
			self.calculate_time()
			self.check_discount()
	
	def on_save(self):
			self.check_discount()

	def calculate_time(self):
		self.start_time = "%s %s" % (self.appointment_date, self.appointment_time)
		self.end_time= datetime.combine(getdate(self.appointment_date), get_time(self.appointment_time)) + timedelta(seconds=flt(self.total_duration))
	
	def check_discount(self):
		if self.membership_status=='Member':
			doc= frappe.get_all('Member Benefits', filters={'client_id': self.client_id, 'benefit_status': 'Active'}, fields=['*'])
			if doc:
				doc_1= doc[0]
				d = flt(doc_1.spa_treatments)
				self.member_discount= flt(self.regular_rate) * d/100.0
				self.rate = flt(self.regular_rate) - flt(self.member_discount)
			else:
				self.member_discount=0.00
				self.rate = flt(self.regular_rate)
		else:
			self.member_discount=0.00
			self.rate = flt(self.regular_rate)
	
	def on_update_after_submit(self):
		if self.club_room:
			room= frappe.get_all('Club Room Schedule', filters={'spa_booking': self.name,}, fields=["*"])
			if room:
				for d in room:
					schedule= frappe.get_doc('Club Room Schedule', d.name)
					schedule.room_name=self.club_room
					schedule.save()
			else:
				doc= frappe.get_doc({
					"doctype": 'Club Room Schedule',
					"room_name": self.club_room,
					"date": self.appointment_date,
					"from_time": self.start_time,
					"to_time": self.end_time,
					"booking_type": 'Spa',
					"spa_booking": self.name
					})
				doc.insert()
				doc.save()
	
	def before_submit(self):
		if self.payment_method=="Wallet":
			wallet= get_balance(self.client_id)
			if wallet < self.rate:
				frappe.throw("Not enough wallet balance")

	def on_submit(self):
		if self.payment_method=="Wallet":	
			doc= frappe.get_doc({
				"doctype": 'Wallet Transaction',
				"client_id": self.client_id,
				"transaction_type": 'Payment',
				"amount": self.rate,
				"payment_type": 'Spa'
			})
			doc.insert()
			doc.submit()
	
	def on_cancel(self):
		self.db_set('status', 'Cancelled')
		if self.payment_method=="Wallet":
			doc= frappe.get_doc({
				"doctype": 'Wallet Transaction',
				"client_id": self.client_id,
				"transaction_type": 'Refund',
				"amount": self.rate,
				"payment_type": 'Spa'
			})
			doc.insert()
			doc.submit()
		self.reload()