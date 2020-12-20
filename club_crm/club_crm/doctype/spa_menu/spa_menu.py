# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SpaMenu(Document):
	def validate(self):
		self.calculate_duration()

	def calculate_duration(self):
		self.total_duration = self.duration + self.turn_over_time