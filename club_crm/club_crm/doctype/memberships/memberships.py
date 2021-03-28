# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from datetime import datetime, timedelta
from frappe.utils import getdate, get_time, flt
from frappe.model.document import Document

class Memberships(Document):
	def validate(self):
		self.set_expiry()
		# self.set_member_number()
		
	def set_expiry(self):
		if type(self.start_date) == str:
			start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
		else:
			start_date = self.start_date
		expiry_date = start_date + timedelta(seconds=float(self.duration))
		self.end_date = expiry_date.strftime("%Y-%m-%d")

	def set_member_number(self):
		if self.client_id_1:
			frappe.db.set_value('Client', self.client_id_1, 'member_id', self.member_no_1)
			frappe.db.set_value('Client', self.client_id_1, 'card_no', self.card_no_1)
			frappe.db.set_value('Client', self.client_id_1, 'membership_no', self.membership_id)
			frappe.db.commit()




