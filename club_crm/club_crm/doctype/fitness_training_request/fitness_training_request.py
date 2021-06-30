# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt, now_datetime
from datetime import datetime, timedelta, date, time
from frappe.model.document import Document
from frappe import _
from club_crm.club_crm.utils.sms_notification import send_sms
from club_crm.club_crm.utils.push_notification import send_push
from club_crm.club_crm.doctype.client_sessions.client_sessions import create_session

class FitnessTrainingRequest(Document):
	def after_insert(self):
		self.trainer_notification()
	
	def validate(self):
		self.validate_table()
		self.calculate_time()
		self.set_payment_details()
		self.create_sessions()
		self.send_notification()

	def validate_table(self):
		if self.request_status == "Scheduled":
			if not self.table_schedule:
				frappe.throw("Please fill your training schedule under the 'Trainer Schedule' section.")
			else:
				no_rows=0
				for row in self.table_schedule:
					no_rows += 1
				if not int(self.number_of_sessions) == no_rows:
					frappe.throw("Number of appointment schedules does not match number of requested sessions")

				duration = 0.0
				package = frappe.get_doc('Club Packages', self.fitness_package)
				if package.package_table:
					for fitness in package.package_table:
						if fitness.service_type=="Fitness Services":
							duration = fitness.validity
				if type(self.start_date) == str:
					start_datetime= datetime.strptime(self.start_date, "%Y-%m-%d")
				else:
					start_datetime = self.start_date
				expiry = start_datetime + timedelta(seconds=duration)
				
				for row in self.table_schedule:
					if type(row.date) == str:
						row_datetime= datetime.strptime(row.date, "%Y-%m-%d")
					else:
						row_datetime = row.date

					if expiry < row_datetime:
						expiry_date = datetime.strftime(expiry, "%d-%m-%Y")
						msg = _('One of the scheduled dates exceeds the validity of the package from the start date. The dates should be within ')
						msg += _('<b>{0}</b>.').format(expiry_date)
						frappe.throw(msg, title=_('Schedule date error'))

		if self.request_status == "Completed":
			if not self.table_schedule:
				frappe.throw("Please fill your training schedule under the 'Trainer Schedule' section.")
			if self.payment_status== "Not Paid":
				frappe.throw("The training request has not been paid yet.")

	def calculate_time(self):
		package = frappe.get_doc('Club Packages', self.fitness_package)
		if package.package_table:
			for row in package.package_table:
				fitness = frappe.get_doc('Fitness Services', row.service_name)
				self.validity = fitness.duration
				
		if self.table_schedule:
			for row in self.table_schedule:
				row.from_time = convert24(row.time_from)
				from_time = datetime.strptime(row.from_time, "%H:%M:%S")
				to_time = from_time + timedelta(seconds=self.validity)
				row.to_time = datetime.strftime(to_time, "%H:%M:%S")
				row.start_datetime = "%s %s" % (row.date, row.from_time or "00:00:00")

	def set_payment_details(self):
		self.paid_amounts = 0.0
		self.total_to_be_paid = self.price
		if self.payment_table:
			for row in self.payment_table:
				self.paid_amounts += row.paid_amount
		self.balance_amount = self.total_to_be_paid - self.paid_amounts
		if self.balance_amount == 0.0:
			frappe.db.set_value("Cart", self.name, "payment_status", "Paid")

	def create_sessions(self):
		if self.sessions_created==0:
			if self.request_status == "Completed" and self.payment_status == "Paid":
				club_package = frappe.get_doc('Club Packages', self.fitness_package)
				if club_package.package_table:
					for row in club_package.package_table:
						fitness = create_session(self.client_id, self.fitness_package, row.service_type, row.service_name, row.no_of_sessions, row.validity)
						if self.table_schedule:
							for schedule in self.table_schedule:
								if type(schedule.start_datetime) == str:
									start_time = datetime.strptime(schedule.start_datetime, "%Y-%m-%d %H:%M:%S")
								else:
									start_time = schedule.start_datetime

								doc = frappe.get_doc({
									"doctype": 'Fitness Training Appointment',
									"session":1,
									"online":1,
									"client_id": self.client_id,
									"session_name": fitness.name,
									"service_staff": self.trainer,
									"start_time" : start_time
								})
								doc.save()
					self.sessions_created = 1
	
	def trainer_notification(self):
		settings = frappe.get_doc('Fitness Training Settings')
		if settings.enabled_trainer==1:
			msg = "New Fitness Training Request has been received from "+self.client_name+"."
			receiver_list='"'+str(self.trainer_mobile_no)+'"'
			send_sms(receiver_list,msg)

	def send_notification(self):
		settings = frappe.get_doc('Fitness Training Settings')
		if settings.enabled_client==1:
			if settings.scheduled_message:
				msg = str(settings.scheduled_message)
			else:
				msg = "Your personalized Fitness Training schedule is ready on the app."

			# Notification for scheduled appointments to Client
			if self.schedule_notification==0 and self.request_status=="Scheduled":
				receiver_list='"'+self.mobile_number+'"'
				send_sms(receiver_list,msg)
				client = frappe.get_doc('Client', self.client_id)
				if client.fcm_token:
					title = "Fitness Training schedule is ready"
					send_push(client.name,title,msg)
				self.schedule_notification=1

@frappe.whitelist()
def convert24(str1):
	if str1[-3:] == " AM" and str1[:2] == "12":
		return "00" + str1[2:-3]
	elif str1[-3:] == " AM":
		return str1[:-3]
	elif str1[-3:] == " PM" and str1[:2] == "12":
		return str1[:-3]
	else:
		return str(int(str1[:2]) + 12) + str1[2:8]