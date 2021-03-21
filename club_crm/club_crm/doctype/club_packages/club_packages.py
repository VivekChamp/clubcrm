# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class ClubPackages(Document):
	def validate(self):
		self.set_total()

	# def set_title(self):
	# 	self.title = self.package_name
	def set_total(self):
		self.total_price = 0.0
		for row in self.package_table:
			self.total_price += row.price