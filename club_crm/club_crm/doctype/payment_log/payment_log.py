# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class PaymentLog(Document):
	def validate(self):
		self.set_title()
	
	def set_title(self):
		self.title = _('{0} {1} for {2}').format(self.req_bill_to_forename, self.req_bill_to_surname, self.req_reference_number)
