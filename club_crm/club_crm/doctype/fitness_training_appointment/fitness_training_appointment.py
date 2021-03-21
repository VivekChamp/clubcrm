# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe.model.document import Document
from frappe.utils import getdate, get_time, flt
from frappe.model.mapper import get_mapped_doc

class FitnessTrainingAppointment(Document):
	# def on_submit(self):
	# 	self.update_sessions_count_in_fitness_training_session()
	
	# def validate(self):
	#     self.set_status()	

	# def on_update_after_submit(self):
	# 	self.update_sessions_count_in_fitness_training_session()

	# def on_cancel(self):
	# 	self.update_sessions_count_in_fitness_training_session(on_cancel=True)

	# def update_sessions_count_in_fitness_training_session(self, on_cancel=False):
	# 	fitness_session = frappe.get_doc('Fitness Training Session', self.fitness_session)
	# 	if self.status == "Scheduled":
	# 		fitness_session.booked_sessions += 1
	# 		fitness_session.save()
	# 	# if self.status =="Open":
	# 	# 	fitness_session.booked_sessions += 1
	# 	# 	fitness_session.save()
	# 	if self.status == "Completed":
	# 		fitness_session.used_sessions += 1
	# 		fitness_session.remaining_sessions -=1
	# 		fitness_session.booked_sessions -= 1
	# 		fitness_session.save()
	# 	if self.status=="No show":
	# 		fitness_session.used_sessions += 1
	# 		fitness_session.remaining_sessions -=1
	# 		fitness_session.save()
	# 	if self.status=="Cancelled":
	# 		fitness_session.booked_sessions -= 1
	# 		fitness_session.save()
	# 	if on_cancel:
	# 		if self.status == "Scheduled":
	# 			fitness_session.booked_sessions -= 1
	# 			fitness_session.save()
	# 		if self.status  =="Open" :
	# 			fitness_session.booked_sessions -= 1
	# 			fitness_session.save()
	# 		if self.status == "Completed":
	# 			fitness_session.used_sessions -= 1
	# 			fitness_session.remaining_sessions +=1
	# 			fitness_session.save()
	# 		if self.status=="No show":
	# 			fitness_session.used_sessions -= 1
	# 			fitness_session.remaining_sessions +=1
	# 			fitness_session.save()
	def set_status(self):
		today = getdate()
		start_time= datetime.strptime(str(self.start_time), '%Y-%m-%d %H:%M:%S')
		date= start_time.date()
		
		if not self.status == "Complete":
			if date == today:
				self.status = "Open"
			elif date > today:
				self.status = "Scheduled"
		if not self.start_time:
			frappe.msgprint({
				title: __('Notification'),
				indicator: 'red',
				message: __('Document updated successfully')
				});


@frappe.whitelist()
def get_trainer_resources():
	trainers= frappe.get_all('Fitness Trainer',fields=['employee_name'])
	resource=[]
	if trainers:
		for trainer in trainers:
			resource.append({
				'id' : trainer.employee_name,
				'title' : trainer.employee_name
			})
	return resource

@frappe.whitelist()
def get_events(start, end, filters=None):

	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions('Fitness Training Appointment', filters)

	data = frappe.db.sql("""
		select
		`tabFitness Training Appointment`.name, `tabFitness Training Appointment`.client_name,
		`tabFitness Training Appointment`.title, `tabFitness Training Appointment`.fitness_trainer,
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
		{"start": start, "end": end}, as_dict=True, update={"textColor": '#fff'})

	return data