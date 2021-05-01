# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

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

	def set_time(self):
		if self.date and self.from_time and self.to_time:
			self.start_time = "%s %s" % (self.date, self.from_time or "00:00:00")
			self.end_time = "%s %s" % (self.date, self.to_time or "00:00:00")
		# if not self.from_time:
		# 	self.from_time = None
		# if not self.to_time:
		# 	self.to_time -= None