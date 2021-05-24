# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import getdate, get_time, flt, now_datetime
from datetime import datetime, timedelta, date, time
from frappe import _
from frappe.model.document import Document
from club_crm.api.wallet import get_balance
from club_crm.club_crm.doctype.client_sessions.client_sessions import check_spa_bookings
from frappe.model.mapper import get_mapped_doc

class SpaAppointment(Document):
	def validate(self):
		self.set_appointment_date_time()
		# self.validate_past_days()
		self.set_addons_and_durations()
		self.set_total_duration()
		if self.online==0:
			self.validate_overlaps()
		self.validate_room_overlaps()
		self.set_prices()
		self.set_status()
		self.set_color()
		self.set_title()
		if self.session==1:
			self.set_paid_and_net_total()

	def after_insert(self):
		if self.session==1:
			self.set_booked_session_count()
		if self.club_room:
			self.create_room_schedule()

	def on_update(self):
		if self.club_room:
			self.create_room_schedule()

	def set_title(self):
		if self.therapist_requested == 1:
			self.title = _('** {0} for {1}').format(self.client_name,self.spa_service)
		else:	
			self.title = _('{0} for {1}').format(self.client_name,self.spa_service)

	def set_appointment_date_time(self):
		if type(self.start_time) == str:
			start_datetime = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		else:
			start_datetime = self.start_time
		self.appointment_date = start_datetime.date()
		self.appointment_time = datetime.strftime(start_datetime, "%H:%M:%S")

	def set_addons_and_durations(self):
		self.addon_duration = 0.0
		self.addon_turnover = 0.0
		self.addon_total_price = 0.0
		self.addon_duration_total = 0.0

		for addon in self.addon_table:
			self.addon_duration += addon.service_duration
			self.addon_turnover += addon.service_turnover
			self.addon_total_price += addon.addon_price

		if self.zero_turnover == 1:
			self.service_turnover = 0.0
		self.total_service_duration = self.service_duration + self.service_turnover

		if self.zero_turnover_addon == 1:
			self.addon_turnover = 0.0
		self.total_addon_duration = self.addon_duration + self.addon_turnover
		self.total_duration = self.total_service_duration + self.total_addon_duration
		#self.net_total = self.default_price + self.addon_total_price
	
	def set_total_duration(self):
		if type(self.start_time) == str:
			start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		else:
			start_datetime = self.start_time
		self.end_time = start_datetime + timedelta(seconds=self.total_duration)
		self.appointment_end_time = datetime.strftime(self.end_time, "%H:%M:%S")
	
	def set_prices(self):
		self.service_amount = self.default_price
		self.addon_amount = self.addon_total_price
		self.net_total = self.service_amount + self.addon_amount

	def set_color(self):
		if self.payment_status == "Not Paid":
			if self.appointment_status=="Scheduled":
				self.color="#39ff9f"
			elif self.appointment_status=="Open":
				self.color="#8549ff"
			elif self.appointment_status=="Checked-in":
				self.color="#ffc107"
			elif self.appointment_status=="No Show":
				self.color="#ff8a8a"
			else:
				self.color="#b22222"
		if self.payment_status == "Paid":
			self.color="#20a7ff"

	def set_booked_session_count(self):
		doc = frappe.get_doc('Client Sessions', self.session_name)
		doc.booked_sessions += 1
		doc.save()

	def before_submit(self):
		if self.payment_method=="Wallet":
			wallet= get_balance()
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
		self.db_set('appointment_status', 'Cancelled')
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

	def set_paid_and_net_total(self):
		self.payment_status = "Paid"
		self.default_price = 0.0

	def set_status(self):
		today = getdate()
		appointment_date = getdate(self.appointment_date)
		# If appointment is created for today set status as Open else Scheduled (only for offline booking)
		if self.appointment_status=="Scheduled" or self.appointment_status =="Open" or self.appointment_status == "Draft":
			if self.online==0:
				if appointment_date == today:
					self.appointment_status = 'Open'
				elif appointment_date > today:
					self.appointment_status = 'Scheduled'
			elif self.online==1:
				if self.payment_status=="Paid":
					if appointment_date == today:
						self.appointment_status = 'Open'
					elif appointment_date > today:
						self.appointment_status = 'Scheduled'
				else:
					self.appointment_status = 'Draft'

	def validate_overlaps(self):
		if type(self.start_time) == str:
			start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		else:
			start_datetime = self.start_time
		end_time = start_datetime + timedelta(seconds=self.total_duration)
		overlaps = frappe.db.sql("""
		select
			name, service_staff, client_name, appointment_time, total_duration, appointment_end_time
		from
			`tabSpa Appointment`
		where
			appointment_date=%s and name!=%s and appointment_status NOT IN ("Cancelled", "No Show")
			and (service_staff=%s or client_name=%s) and
			((appointment_time<%s and appointment_end_time>%s) or
			(appointment_time>%s and appointment_time<%s) or
			(appointment_time>%s and appointment_end_time<%s) or
			(appointment_time=%s))
		""", (self.appointment_date, self.name, self.service_staff, self.client_name,
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
	
	def validate_room_overlaps(self):
		overlaps = frappe.db.sql("""
		select
			name,room_name, from_time, to_time
		from
			`tabClub Room Schedule`
		where
			room_name=%s and name=!%s and
			((from_time<%s and to_time>%s) or
			(from_time>%s and from_time<%s) or
			(from_time>%s and to_time<%s) or
			(from_time=%s))
		""", (self.club_room, self.name,
		self.start_time, self.start_time,
		self.start_time, self.end_time, 
		self.start_time, self.end_time,
		self.start_time))

		if overlaps:
			overlapping_details = _('This spa room is already booked for another appointment from ')
			overlapping_details += _('<b>{0}</b> to <b>{1}</b>').format(
				overlaps[0][1], overlaps[0][2])
			frappe.throw(overlapping_details, title=_('Room Overlap'))

	# def validate_past_days(self):
	# 	today = date.today()
	# 	if self.appointment_date < today:
	# 		past_day = _('Appointments cannot be created for a past date')
	# 		frappe.throw(past_day, title=_('Appointment Date Error'))
	
	def create_room_schedule(self):
		room= frappe.get_all('Club Room Schedule', filters={'spa_booking': self.name}, fields=["*"])
		if room:
			for d in room:
				schedule= frappe.get_doc('Club Room Schedule', d.name)
				schedule.room_name=self.club_room
				schedule.from_time=self.start_time
				schedule.to_time=self.end_time
				schedule.booking_type= "Spa"
				schedule.spa_booking= self.name
				schedule.save()
		else:
			doc= frappe.get_doc({
				"doctype": 'Club Room Schedule',
				"room_name": self.club_room,
				"from_time": self.start_time,
				"to_time": self.end_time,
				"booking_type": 'Spa',
				"spa_booking": self.name
			})
			doc.insert()
			doc.save()

@frappe.whitelist()
def update_appointment_status():
	# update the status of appointments daily
	today = getdate()
	appointments = frappe.get_all('Spa Appointment', filters={'appointment_status': ('not in', ['Draft', 'Complete', 'Cancelled', 'Checked-in', 'No Show']), 'docstatus': 0}, fields=['name','appointment_status','online','appointment_date'])
	for appointment in appointments:
		# spa_app = frappe.get_doc('Spa Appointment', appointment.name)
		appointment_date = getdate(appointment.appointment_date)

		# If appointment is created for today set status as Open else Scheduled (only for offline booking)
		if appointment.appointment_status=="Scheduled" or appointment.appointment_status =="Open":
			if appointment.online==0:
				if appointment_date == today:
					frappe.db.set_value('Spa Appointment', appointment.name, 'appointment_status', 'Open')
					frappe.db.commit()
				elif appointment_date > today:
					frappe.db.set_value('Spa Appointment', appointment.name, 'appointment_status', 'Scheduled')
					frappe.db.commit()
				elif appointment_date < today:
					frappe.db.set_value('Spa Appointment', appointment.name, 'appointment_status', 'No Show')
					frappe.db.commit()

			elif appointment.online==1:
				if appointment_date == today:
					frappe.db.set_value('Spa Appointment', appointment.name, 'appointment_status', 'Open')
					frappe.db.commit()
				elif appointment_date > today:
					frappe.db.set_value('Spa Appointment', appointment.name, 'appointment_status', 'Scheduled')
					frappe.db.commit()
				elif appointment_date < today:
					frappe.db.set_value('Spa Appointment', appointment.name, 'appointment_status', 'No Show')
					frappe.db.commit()

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
	frappe.db.set_value('Spa Appointment', appointment_id, 'appointment_status', status)
	cancel_appointment(appointment_id)

@frappe.whitelist()
def cancel_appointment(appointment_id):
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	frappe.db.set_value("Spa Appointment",appointment_id,"appointment_status","Cancelled")
	frappe.db.set_value("Spa Appointment",appointment_id,"color","#b22222")
	frappe.db.set_value("Spa Appointment",appointment_id,"docstatus",2)

	if appointment.session==1:
		doc = frappe.get_doc('Client Sessions', appointment.session_name)
		doc.booked_sessions -= 1
		doc.save()
	
	if appointment.online == 1:
		frappe.db.set_value('Cart', appointment.cart, 'payment_status', 'Cancelled')
		frappe.db.commit()

	# if appointment.payment_status == "Paid":

	# 	doc= frappe.get_doc({
	# 		"doctype": 'Wallet Transaction',
	# 		"client_id": appointment.client_id,
	# 		"transaction_type": 'Refund',
	# 		"amount": appointment.rate,
	# 		"payment_type": 'Spa'
	# 	})
	# 	doc.insert()
	# 	doc.submit()

@frappe.whitelist()
def no_show(appointment_id):
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	frappe.db.set_value("Spa Appointment",appointment_id,"appointment_status","No Show")
	# frappe.db.set_value("Spa Appointment",appointment_id,"color","#ff8a8a")
	frappe.db.set_value("Spa Appointment",appointment_id,"docstatus",2)

	if appointment.session==1:
		doc = frappe.get_doc('Client Sessions', appointment.session_name)
		doc.used_sessions += 1
		doc.booked_sessions -= 1
		doc.save()

@frappe.whitelist()
def complete(appointment_id):
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	frappe.db.set_value("Spa Appointment",appointment_id,"appointment_status","Complete")
	# frappe.db.set_value("Spa Appointment",appointment_id,"color","#20a7ff")
	frappe.db.set_value("Spa Appointment",appointment_id,"docstatus",1)
	doc = frappe.get_doc('Check In', appointment.checkin_document)
	doc.check_out_time = now_datetime()
	doc.save()

	if appointment.session==1:
		doc = frappe.get_doc('Client Sessions', appointment.session_name)
		doc.used_sessions += 1
		doc.booked_sessions -= 1
		doc.save()

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
	# roles = frappe.get_roles()
	# all_therapist = True
	# for role in roles:
	# 	if role == "Spa Staff":
	# 		all_therapist = False
	# 		break
	
	# if all_therapist:
	therapists = frappe.get_all('Service Staff', filters={'spa_check':1}, fields=['display_name'], order_by="display_name asc")
	resource=[]
	if therapists:
		for therapist in therapists:
			resource.append({
				'id' : therapist.display_name,
				'title' : therapist.display_name
			})
	# else:
	# 	therapists = frappe.get_all('Service Staff', filters={'spa_check':1, 'email': frappe.session.user}, fields=['display_name'])
	# 	resource=[]
	# 	if therapists:
	# 		for therapist in therapists:
	# 			resource.append({
	# 				'id' : therapist.display_name,
	# 				'title' : therapist.display_name
	# 			})
	return resource

@frappe.whitelist()
def get_events(start, end, filters=None):

	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions('Spa Appointment', filters)

	events = []
	data = frappe.db.sql("""
		select
		`tabSpa Appointment`.name, `tabSpa Appointment`.client_name,
		`tabSpa Appointment`.title, `tabSpa Appointment`.service_staff,
		`tabSpa Appointment`.payment_status,
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
		and `tabSpa Appointment`.appointment_status != 'Cancelled' {conditions}""".format(conditions=conditions),
		{"start": start, "end": end}, as_dict=True, update={"rendering": ''})
	
	for item in data:
		events.append(item)
	
	bg_event = frappe.db.sql("""
		select
		`tabDay Schedule`.start_time,
		`tabDay Schedule`.end_time,
		`tabDay Schedule`.service_staff

		from
		`tabDay Schedule`

		where
		(`tabDay Schedule`.date between %(start)s and %(end)s)
		and `tabDay Schedule`.parenttype = 'Service Staff Availability' {conditions}""".format(conditions=conditions),
		{"start": start, "end": end}, as_dict=True, update={"rendering": 'background'})

	for item in bg_event:
		events.append(item)

	return events

@frappe.whitelist()
def get_therapist_spa_service(spa_service):
	spa_services = frappe.get_doc('Spa Services', spa_service)

	therapist_data = frappe.db.get_all('Spa Services Assignment', {'spa_group': spa_services.spa_group}, ['parent as service_staff'])
	if therapist_data:
		return therapist_data
	# therapists = []
	# therapist_list = frappe.get_all('Service Staff', filters={'spa_check':1})
	# if therapist_list:
	# 	for therapist in therapist_list:
	# 		doc = frappe.get_doc('Service Staff', therapist.name)
	# 		if doc.spa_service_assignment:
	# 			for spa in doc.spa_service_assignment:
	# 				if spa.spa_group == spa_services.spa_group:
	# 					therapists.append({
	# 						"name": therapist.name
	# 						})
	# return therapists
	return {}

@frappe.whitelist()
def get_club_room(doctype, txt, searchfield, start, page_len, filters):
	available_rooms =[]
	club_room_list = frappe.db.get_list('Club Room', {'club_room_type': 'Spa','is_group':0}, ['name'])

	for room in club_room_list:
		if not frappe.db.get_value('Club Room Schedule', {'room_name': room["name"],'from_time': ['>=', filters['from_time']],'to_time': ['<=', filters['to_time']]}, 'name'):
			available_rooms.append([room['name']])
	
	return available_rooms
