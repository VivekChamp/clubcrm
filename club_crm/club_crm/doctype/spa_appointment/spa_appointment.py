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
	def validate(self):
		self.set_status()
		self.calculate_time()
		self.check_discount()
		#self.validate_overlaps()
		if self.club_room:
			self.create_room_schedule()
	
	def after_insert(self):
		self.reload()
		#invoice_appointment(self)

	# def before_submit(self):
	# 		self.calculate_time()
	# 		self.check_discount()
	
	# def on_save(self):
	# 		self.calculate_time()
	# 		self.check_discount()

	def calculate_time(self):
		self.start_time = "%s %s" % (self.appointment_date, self.appointment_time)
		self.end_time = datetime.combine(getdate(self.appointment_date), get_time(self.appointment_time)) + timedelta(seconds=self.total_duration)
	
	def check_discount(self):
		if self.membership_status=='Member':
			doc = frappe.get_all('Member Benefits', filters={'client_id': self.client_id, 'benefit_status': 'Active'}, fields=['*'])
			if doc:
				doc_1= doc[0]
				if doc_1.spa_treatments and float(doc_1.spa_treatments) > 0:
					d = float(doc_1.spa_treatments)
					member_discount = float(self.regular_rate) * d/100.0
					self.member_discount = int(member_discount//5*5)
				else:
					self.member_discount = int(0)
			else:
				self.member_discount = int(0)
		else:
			self.member_discount = int(0)
		self.rate = self.regular_rate - self.member_discount
		return self.member_discount

	def create_room_schedule(self):
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

	def set_status(self):
		today = getdate()
		appointment_date = getdate(self.appointment_date)

		# If appointment is created for today set status as Open else Scheduled (only for offline booking)
		if not self.status=="Complete":
			if self.online==0:
				if appointment_date == today:
					self.status = 'Open'
				elif appointment_date > today:
					self.status = 'Scheduled'
			elif self.online==1:
				if self.payment_status=="Paid":
					if appointment_date == today:
						self.status = 'Open'
					elif appointment_date > today:
						self.status = 'Scheduled'
				else:
					self.status = 'Draft'

def update_appointment_status():
	# update the status of appointments daily
	appointments = frappe.get_all('Spa Appointment', {
		'status': ('not in', ['Draft', 'Complete', 'Cancelled'])
	}, as_dict=1)

	for appointment in appointments:
		frappe.get_doc('Spa Appointment', appointment.name).set_status()

# def invoice_appointment(appointment_doc):
# 	if appointment_doc.payment_status=="Paid":

# 		sales_invoice = frappe.new_doc('Sales Invoice')
# 		sales_invoice.client_id = appointment_doc.client_id
# 		sales_invoice.customer = frappe.get_value('Client', appointment_doc.client_id, 'customer')
# 		sales_invoice.spa_booking_id = appointment_doc.name

# 		item = sales_invoice.append('items', {})
# 		item = get_appointment_item(appointment_doc, item)

# 		# Add payments if payment details are supplied else proceed to create invoice as Unpaid
# 		if appointment_doc.mode_of_payment and appointment_doc.paid_amount:
# 			sales_invoice.is_pos = 1
# 			payment = sales_invoice.append('payments', {})
# 			payment.mode_of_payment = appointment_doc.mode_of_payment
# 			payment.amount = appointment_doc.paid_amount

# 		sales_invoice.set_missing_values(for_validate=True)
# 		sales_invoice.flags.ignore_mandatory = True
# 		sales_invoice.save(ignore_permissions=True)
# 		sales_invoice.submit()
# 		frappe.msgprint(_('Sales Invoice {0} created'.format(sales_invoice.name)), alert=True)
# 		frappe.db.set_value('Patient Appointment', appointment_doc.name, 'invoiced', 1)
# 		frappe.db.set_value('Patient Appointment', appointment_doc.name, 'ref_sales_invoice', sales_invoice.name)

@frappe.whitelist()
def update_status(appointment_id, status):
	frappe.db.set_value('Spa Appointment', appointment_id, 'status', status)
	cancel_appointment(appointment_id)

def cancel_appointment(appointment_id):
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	# if appointment.invoiced:
	# 	sales_invoice = check_sales_invoice_exists(appointment)
	# 	if sales_invoice and cancel_sales_invoice(sales_invoice):
	# 		msg = _('Appointment {0} and Sales Invoice {1} cancelled').format(appointment.name, sales_invoice.name)
	# 	else:
	# 		msg = _('Appointment Cancelled. Please review and cancel the invoice {0}').format(sales_invoice.name)
	# else:
	# 	fee_validity = manage_fee_validity(appointment)
	# 	msg = _('Appointment Cancelled.')
	# 	if fee_validity:
	# 		msg += _('Fee Validity {0} updated.').format(fee_validity.name)

	# frappe.msgprint(msg)