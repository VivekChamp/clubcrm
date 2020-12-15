# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CheckIn(Document):
	def on_submit(self):
		if self.check_in_type=="Group Class":
			frappe.db.set_value('Group Class Attendees', self.class_attendee_id,'checked_in', 'Yes')



