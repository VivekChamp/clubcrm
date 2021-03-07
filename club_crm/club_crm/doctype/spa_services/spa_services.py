# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class SpaServices(Document):
	def validate(self):
		self.set_total_duration()

	def set_total_duration(self):
		self.total_duration = self.duration + self.turn_over_time
