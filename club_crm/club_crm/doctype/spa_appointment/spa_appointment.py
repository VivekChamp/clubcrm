# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date, time
from frappe import _
from frappe.model.document import Document
from club_crm.api.wallet import get_balance

class SpaAppointment(Document):
	def validate(self):
		self.set_appointment_date_time()
		self.set_addons_and_durations()
		self.set_total_duration()
		self.validate_overlaps()
		self.check_discount()
		self.set_status()
		self.set_color()
		self.set_title()
		# if self.club_room:
		#  	self.create_room_schedule()

	def set_title(self):
		self.title = _('{0} for {1}').format(self.client_name,
			self.spa_service)

	def set_appointment_date_time(self):
		start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		self.appointment_date = start_datetime.date()
		self.appointment_time = datetime.strftime(start_datetime, "%H:%M:%S")

	def set_addons_and_durations(self):
		self.addon_duration=0
		self.addon_turnover=0
		self.addon_total_price=0
		self.addon_duration_total=0

		for addon in self.addon_table:
			self.addon_duration += addon.service_duration
			self.addon_turnover += addon.service_turnover
			self.addon_total_price += addon.addon_price

		self.total_service_duration = self.service_duration + self.service_turnover
		self.total_addon_duration = self.addon_duration + self.addon_turnover
		self.total_duration = self.total_service_duration + self.total_addon_duration
		self.net_total = self.default_price + self.addon_total_price
	
	def set_total_duration(self):
		start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		self.end_time = start_datetime + timedelta(seconds=self.total_duration)
		self.appointment_end_time = datetime.strftime(self.end_time, "%H:%M:%S")
	
	def check_discount(self):
		self.member_discount = float(0)
		if self.member_discount_check==1:
			if self.membership_status=='Member':
				member_discount = self.default_price * 0.25
				self.member_discount = float(member_discount//0.5*0.5)
				# doc = frappe.get_all('Member Benefits', filters={'client_id': self.client_id, 'benefit_status': 'Active'}, fields=['*'])
				# if doc:
				# 	doc_1= doc[0]
				# 	if doc_1.spa_treatments and float(doc_1.spa_treatments) > 0:
				# 		d = float(doc_1.spa_treatments)
				# 		member_discount = float(self.default_price) * d/100.0
				# 		self.member_discount = int(member_discount//5*5)
				# 	else:
				# 		self.member_discount = int(0)
				# else:
				# 	self.member_discount = int(0)

		if self.apply_discount=="Amount":
			self.discount_percentage = 0
		elif self.apply_discount=="Percentage on Net Total":
			self.discount_amount =  (self.net_total * self.discount_percentage) / 100
		elif self.apply_discount=="Percentage on Net Total after member discount":
			discounted_total = self.net_total - self.member_discount
			self.discount_amount = (discounted_total * self.discount_percentage) / 100
		else:
			self.discount_percentage = 0
			self.discount_amount = 0
		self.grand_total = self.net_total - self.member_discount - self.discount_amount
		return self.member_discount

	def set_color(self):
		if self.appointment_status=="Scheduled":
			self.color="yellow"
		elif self.appointment_status=="Open":
			self.color="orange"
		elif self.appointment_status=="Checked-in":
			self.color="lightblue"
		elif self.appointment_status=="Complete":
			self.color="green"
		elif self.appointment_status=="No show":
			self.color="grey"
		else:
			self.color="red"

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
		#appointment_date = getdate(self.appointment_date)

		# If appointment is created for today set status as Open else Scheduled (only for offline booking)
		if self.appointment_status=="Scheduled" or self.appointment_status =="Open":
			if self.online==0:
				if self.appointment_date == today:
					self.appointment_status = 'Open'
				elif self.appointment_date > today:
					self.appointment_status = 'Scheduled'
			elif self.online==1:
				if self.payment_status=="Paid":
					if self.appointment_date == today:
						self.appointment_status = 'Open'
					elif self.appointment_date > today:
						self.appointment_status = 'Scheduled'
				else:
					self.appointment_status = 'Draft'

	def validate_overlaps(self):
		start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		end_time = start_datetime + timedelta(seconds=self.total_duration)
		overlaps = frappe.db.sql("""
		select
			name, spa_therapist, client_name, appointment_time, total_duration, appointment_end_time
		from
			`tabSpa Appointment`
		where
			appointment_date=%s and name!=%s and status NOT IN ("Complete", "Cancelled")
			and (spa_therapist=%s or client_name=%s) and
			((appointment_time<%s and appointment_end_time>%s) or
			(appointment_time>%s and appointment_time<%s) or
			(appointment_time>%s and appointment_end_time<%s) or
			(appointment_time=%s))
		""", (self.appointment_date, self.name, self.spa_therapist, self.client_name,
		self.appointment_time, self.appointment_time,
		self.appointment_time, self.appointment_end_time, 
		self.appointment_time, self.appointment_end_time,
		self.appointment_time))

		if overlaps:
			overlapping_details = _('Appointment overlaps with ')
			overlapping_details += "<b><a href='/desk#Form/Spa Appointment/{0}'>{0}</a></b>.<br>".format(overlaps[0][0])
			overlapping_details += _('<b>{0}</b> has appointment scheduled with <b>{1}</b> at {2} until {4}.').format(
				overlaps[0][1], overlaps[0][2], overlaps[0][3], overlaps[0][4], overlaps[0][5])
			frappe.throw(overlapping_details, title=_('Appointments Overlapping'))

def update_appointment_status():
	# update the status of appointments daily
	appointments = frappe.get_all('Spa Appointment', {
		'status': ('not in', ['Draft', 'Complete', 'Cancelled', 'Checked in'])
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

@frappe.whitelist()
def cancel_appointment(appointment_id):
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	if appointment.payment_status == "Not Paid":
		frappe.db.set_value("Spa Appointment",appointment_id,"appointment_status","Cancelled")

	#For cancellation
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

@frappe.whitelist()
def get_therapist_resources():
	therapists= frappe.get_all('Spa Therapist',fields=['employee_name'])
	resource=[]
	if therapists:
		for therapist in therapists:
			resource.append({
				'id' : therapist.employee_name,
				'title' : therapist.employee_name
			})
	return resource

@frappe.whitelist()
def get_events(start, end, filters=None):

	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions('Spa Appointment', filters)

	data = frappe.db.sql("""
		select
		`tabSpa Appointment`.name, `tabSpa Appointment`.client_name,
		`tabSpa Appointment`.title, `tabSpa Appointment`.spa_therapist,
		`tabSpa Appointment`.appointment_status,
		`tabSpa Appointment`.total_duration,
		`tabSpa Appointment`.notes,
		`tabSpa Appointment`.start_time,
		`tabSpa Appointment`.end_time,
		`tabSpa Appointment`.color
		from
		`tabSpa Appointment`
		where
		(`tabSpa Appointment`.appointment_date between %(start)s and %(end)s)
		and `tabSpa Appointment`.appointment_status != 'Cancelled' and `tabSpa Appointment`.docstatus < 2 {conditions}""".format(conditions=conditions),
		{"start": start, "end": end}, as_dict=True)

	return data