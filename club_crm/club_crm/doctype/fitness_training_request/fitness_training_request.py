# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.utils import getdate, get_time, flt, now_datetime
from datetime import datetime, timedelta, date, time
from frappe.model.document import Document

class FitnessTrainingRequest(Document):
	def after_insert(self):
		self.send_notification()
	
	def validate(self):
		self.calculate_time()
	# # 	self.set_no_of_sessions()

	def send_notification(self):
		settings = frappe.get_doc('Fitness Training Settings')
		if settings.enabled==1:
			msg = "New Fitness Training Request has been received from "+self.client_name+"."
			receiver_list='"'+self.trainer_mobile_no+'"'
			send_sms(receiver_list,msg)

	def calculate_time(self):
		if self.table_schedule:
			for row in self.table_schedule:
				row.from_time = "%s" % (row.time_from or "00:00:00")
				row.to_time = "%s" % (row.time_to or "00:00:00")
