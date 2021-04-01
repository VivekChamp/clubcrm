# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OnlineOrder(Document):
	def validate(self):
		self.set_total_and_quantity()

	def set_total_and_quantity(self):
		self.total_quantity = 0
		self.total_amount = 0.0

		if self.item:
			for row in self.item:
				row.amount = float(row.rate) * float(row.quantity)
				self.total_quantity += int(row.quantity)
				self.total_amount += row.amount
