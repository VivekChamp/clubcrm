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
		if not self.end_date:
			start_date= datetime.strptime(self.start_date, "%Y-%m-%d")
			expiry_date= start_date + timedelta(days=int(self.duration))
			self.end_date= expiry_date.strftime("%Y-%m-%d")

