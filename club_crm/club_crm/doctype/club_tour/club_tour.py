# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from club_crm.club_crm.utils.sms_notification import send_sms
from club_crm.club_crm.utils.push_notification import send_push
from club_crm.club_crm.doctype.push_notification_center.push_notification_center import send_push_updates

class ClubTour(Document):
	def before_insert(self):
		doc= frappe.get_all('Club Tour', filters={'client_id':self.client_id, 'tour_status': "Pending"})
		if doc:
			frappe.throw('A pending club tour booking already exists. Kindly wait until it is reviewed.')	
		doc= frappe.get_all('Club Tour', filters={'client_id':self.client_id, 'tour_status': "Scheduled"})
		if doc:
			frappe.throw('A scheduled club tour booking already exists. Kindly wait until it is completed.')

	def validate(self):
		self.set_time()

	def on_update(self):
		self.send_notification()

	def set_time(self):
		if self.date and self.from_time and self.to_time:
			self.start_time = "%s %s" % (self.date, self.from_time or "00:00:00")
			self.end_time = "%s %s" % (self.date, self.to_time or "00:00:00")
	
	def send_notification(self):
		if self.tour_status == "Scheduled":
			title = "Book a Tour update"
			message = "You have an update on your club tour appointment"
			client = frappe.get_doc('Client', self.client_id)
			if client.fcm_token:
				send_push(client.name, title, message)
			
			cec_list = frappe.get_all('Service Staff', filters={'display_name': self.assign_cec})
			msg = "You have been assigned for a new Club Tour - "+self.name+"."
			if cec_list:
				for cec in cec_list:
					receiver_list='"'+str(cec.mobile_no)+'"'
					send_sms(receiver_list,msg)