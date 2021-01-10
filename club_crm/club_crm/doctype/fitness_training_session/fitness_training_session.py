# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FitnessTrainingSession(Document):
	def before_save(self):
        	self.remaining_sessions = self.number_of_sessions - self.used_sessions
