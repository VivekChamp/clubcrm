# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt, now_datetime
from datetime import datetime, timedelta, date, time
from frappe import _
from frappe.model.document import Document
from club_crm.api.wallet import get_balance

class FitnessTrainingAppointment(Document):
	def validate(self):
		if self.session==1:
			self.set_paid_and_net_total()
		self.set_appointment_date_time()
		if self.online != 1:
			self.validate_session_expiry()
		# self.validate_past_days()
		self.set_total_duration()
		self.validate_overlaps()
		self.set_prices()
		self.set_status()
		self.set_title()

	def before_insert(self):
		if self.online != 1:
			self.validate_session_count()

	def after_insert(self):
		if self.session==1:
			self.set_booked_session_count()

	def set_appointment_date_time(self):
		if type(self.start_time) == str:
			start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		else:
			start_datetime = self.start_time

		self.appointment_date = start_datetime.date()
		self.appointment_time = datetime.strftime(start_datetime, "%H:%M:%S")
	
	def validate_past_days(self):
		today = date.today()
		if self.appointment_date < today:
			past_day = _('Appointments cannot be created for a past date')
			frappe.throw(past_day, title=_('Appointment Date Error'))

	def set_total_duration(self):
		self.total_duration = self.service_duration
		if type(self.start_time) == str:
			start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		else:
			start_datetime = self.start_time
		self.end_time = start_datetime + timedelta(seconds=self.total_duration)
		self.appointment_end_time = datetime.strftime(self.end_time, "%H:%M:%S")	

	def set_prices(self):
		self.net_total = self.default_price

	def set_status(self):
		today = getdate()
		# If appointment is created for today set status as Open else Scheduled (only for offline booking)
		if self.appointment_status=="Scheduled" or self.appointment_status =="Open":
			if self.online==0:
				if self.appointment_date == today:
					self.appointment_status = 'Open'
				elif self.appointment_date > today:
					self.appointment_status = 'Scheduled'
				elif self.appointment_date < today:
					self.appointment_status = 'No Show'
			elif self.online==1:
				if self.payment_status=="Paid":
					if self.appointment_date == today:
						self.appointment_status = 'Open'
					elif self.appointment_date > today:
						self.appointment_status = 'Scheduled'
					elif self.appointment_date < today:
						self.appointment_status = 'No Show'
				else:
					self.appointment_status = 'Draft'
	
	def set_color(self):
		if self.appointment_status=="Scheduled":
			self.color="#39ff9f"
		elif self.appointment_status=="Open":
			self.color="#8549ff"
		elif self.appointment_status=="Checked-in":
			self.color="#ffc107"
		elif self.appointment_status=="Completed":
			self.color="#20a7ff"
		elif self.appointment_status=="No Show":
			self.color="#ff8a8a"
		else:
			self.color="#b22222"
	
	def set_title(self):
		self.title = _('{0} for {1}').format(self.client_name,
			self.fitness_service)

	def set_paid_and_net_total(self):
		self.payment_status = "Paid"
		self.default_price = 0.0
		self.net_total = 0.0

	def set_booked_session_count(self):
		doc = frappe.get_doc('Client Sessions', self.session_name)
		doc.booked_sessions += 1
		doc.save()
	
	def validate_overlaps(self):
		if type(self.start_time) == str:
			start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		else:
			start_datetime= self.start_time
		end_time = start_datetime + timedelta(seconds=self.total_duration)
		overlaps = frappe.db.sql("""
		select
			name, service_staff, client_name, appointment_time, total_duration, appointment_end_time
		from
			`tabFitness Training Appointment`
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
			overlapping_details += "<b><a href='/desk#Form/Fitness Training Appointment/{0}'>{0}</a></b>.<br>".format(overlaps[0][0])
			overlapping_details += _('<b>{0}</b> has appointment scheduled with <b>{1}</b> at {2} until {4}.').format(
				overlaps[0][1], overlaps[0][2], overlaps[0][3], overlaps[0][4], overlaps[0][5])
			frappe.throw(overlapping_details, title=_('Appointments Overlapping'))

	def validate_session_expiry(self):
		session = frappe.get_doc('Client Sessions', self.session_name)
		if type(self.start_time) == str:
			start_datetime= datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
		else:
			start_datetime = self.start_time
		start = start_datetime.date()

		if start > session.expiry_date:
			expiry = datetime.strftime(session.expiry_date, "%d-%m-%Y")
			msg = _('The appointment date exceeds the expiry date of the package. This package expires on ')
			msg += _('<b>{0}</b>').format(expiry)
			frappe.throw(msg, title=_('Appointment date error'))
	
	def validate_session_count(self):
		session = frappe.get_doc('Client Sessions', self.session_name)
		balance = int(session.remaining_sessions) - int(session.booked_sessions)
		if balance == 0:
			frappe.throw(msg="All remaining sessions in this package are already booked.", title='Error')

@frappe.whitelist()
def no_show(appointment_id):
	appointment = frappe.get_doc('Fitness Training Appointment', appointment_id)
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"appointment_status","No Show")
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"color","#ff8a8a")
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"docstatus",2)

	if appointment.session==1:
		doc = frappe.get_doc('Client Sessions', appointment.session_name)
		doc.used_sessions += 1
		doc.booked_sessions -= 1
		doc.save()

	frappe.msgprint(msg="Appointment marked as 'No Show'", title='Success')

@frappe.whitelist()
def complete(appointment_id):
	appointment = frappe.get_doc('Fitness Training Appointment', appointment_id)
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"appointment_status","Completed")
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"color","#20a7ff")
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"docstatus",1)
	doc = frappe.get_doc('Check In', appointment.checkin_document)
	doc.check_out_time = now_datetime()
	doc.save()

	if appointment.session==1:
		sess = frappe.get_doc('Client Sessions', appointment.session_name)
		sess.used_sessions += 1
		sess.booked_sessions -= 1
		sess.save()
	
	frappe.msgprint(msg="Appointment marked as 'Completed'", title='Success')

@frappe.whitelist()
def cancel_appointment(appointment_id):
	appointment = frappe.get_doc('Fitness Training Appointment', appointment_id)
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"appointment_status","Cancelled")
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"color","#b22222")
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"docstatus",2)

	if appointment.session==1:
		doc = frappe.get_doc('Client Sessions', appointment.session_name)
		doc.booked_sessions -= 1
		doc.save()
	
	frappe.msgprint(msg="Appointment has been cancelled", title='Success')

@frappe.whitelist()
def get_trainer_resources():
	roles = frappe.get_roles()
	all_trainer = True
	for role in roles:
		if role == "Fitness Trainer" or role == "Fitness Staff":
			all_trainer = False
			break
	
	if all_trainer:
		trainers = frappe.get_all('Service Staff', filters={'fitness_check':1}, fields=['display_name'], order_by="display_name asc")
		resource=[]
		if trainers:
			for trainer in trainers:
				resource.append({
					'id' : trainer.display_name,
					'title' : trainer.display_name
				})
	else:
		trainers = frappe.get_all('Service Staff', filters={'fitness_check':1, 'email': frappe.session.user}, fields=['display_name'])
		resource=[]
		if trainers:
			for trainer in trainers:
				resource.append({
					'id' : trainer.display_name,
					'title' : trainer.display_name
				})
	return resource

@frappe.whitelist()
def get_events(start, end, filters=None):
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions('Fitness Training Appointment', filters)

	roles = frappe.get_roles()
	all_trainer = True
	for role in roles:
		if role == "Fitness Trainer" or role == "Fitness Staff":
			all_trainer = False
			break
	
	if all_trainer:
		data = frappe.db.sql("""
			select
			`tabFitness Training Appointment`.name, `tabFitness Training Appointment`.client_name,
			`tabFitness Training Appointment`.title, `tabFitness Training Appointment`.service_staff,
			`tabFitness Training Appointment`.appointment_status,
			`tabFitness Training Appointment`.total_duration,
			`tabFitness Training Appointment`.notes,
			`tabFitness Training Appointment`.start_time,
			`tabFitness Training Appointment`.end_time,
			`tabFitness Training Appointment`.color
			from
			`tabFitness Training Appointment`
			where
			(`tabFitness Training Appointment`.appointment_date between %(start)s and %(end)s)
			and `tabFitness Training Appointment`.appointment_status != 'Cancelled' {conditions}""".format(conditions=conditions),
			{"start": start, "end": end}, as_dict=True)
		return data
	
	else:
		trainers = frappe.get_all('Service Staff', filters={'fitness_check':1, 'email': frappe.session.user}, fields=['display_name'])
		if trainers:
			for trainer in trainers:
				data = frappe.db.sql("""
					select
					`tabFitness Training Appointment`.name, `tabFitness Training Appointment`.client_name,
					`tabFitness Training Appointment`.title, `tabFitness Training Appointment`.service_staff,
					`tabFitness Training Appointment`.appointment_status,
					`tabFitness Training Appointment`.total_duration,
					`tabFitness Training Appointment`.notes,
					`tabFitness Training Appointment`.start_time,
					`tabFitness Training Appointment`.end_time,
					`tabFitness Training Appointment`.color
					from
					`tabFitness Training Appointment`
					where
					(`tabFitness Training Appointment`.appointment_date between %(start)s and %(end)s)
					and (`tabFitness Training Appointment`.service_staff = %(staff)s)
					and `tabFitness Training Appointment`.appointment_status != 'Cancelled' {conditions}""".format(conditions=conditions),
					{"start": start, "end": end, "staff": trainer.display_name}, as_dict=True)
				return data

@frappe.whitelist()
def update_appointment_status():
	# update the status of appointments daily
	today = getdate()
	appointments = frappe.get_all('Fitness Training Appointment', filters={'appointment_status': ('not in', ['Completed', 'Cancelled', 'Checked-in', 'No Show']), 'docstatus': 0}, fields=['name','appointment_status','online','session','appointment_date', 'session_name'])
	for appointment in appointments:
		appointment_date = getdate(appointment.appointment_date)

		# If appointment is created for today set status as Open else Scheduled (only for offline booking)
		if appointment.appointment_status=="Scheduled" or appointment.appointment_status =="Open":
			if appointment.online==0:
				if appointment_date == today:
					frappe.db.set_value('Fitness Training Appointment', appointment.name, 'appointment_status', 'Open')
					frappe.db.commit()
				elif appointment_date > today:
					frappe.db.set_value('Fitness Training Appointment', appointment.name, 'appointment_status', 'Scheduled')
					frappe.db.commit()
				elif appointment_date < today:
					frappe.db.set_value('Fitness Training Appointment', appointment.name, 'appointment_status', 'No Show')
					frappe.db.commit()
					if appointment.session==1:
						session = frappe.get_doc('Client Sessions', appointment.session_name)
						session.used_sessions += 1
						session.booked_sessions -= 1
						session.save()

			elif appointment.online==1:
				if appointment_date == today:
					frappe.db.set_value('Fitness Training Appointment', appointment.name, 'appointment_status', 'Open')
					frappe.db.commit()
				elif appointment_date > today:
					frappe.db.set_value('Fitness Training Appointment', appointment.name, 'appointment_status', 'Scheduled')
					frappe.db.commit()
				elif appointment_date < today:
					frappe.db.set_value('Fitness Training Appointment', appointment.name, 'appointment_status', 'No Show')
					frappe.db.commit()
					if appointment.session==1:
						session = frappe.get_doc('Client Sessions', appointment.session_name)
						session.used_sessions += 1
						session.booked_sessions -= 1
						session.save()

@frappe.whitelist()
def cancel_appointment_online(appointment_id):
	appointment = frappe.get_doc('Fitness Training Appointment', appointment_id)
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"appointment_status","Cancelled")
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"docstatus",2)

	if appointment.session==1:
		doc = frappe.get_doc('Client Sessions', appointment.session_name)
		doc.booked_sessions -= 1
		doc.save()
		
	return 1