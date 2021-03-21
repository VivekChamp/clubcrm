# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SpaServices(Document):
	def validate(self):
		self.set_total_duration()
		#self.set_item()

	def set_total_duration(self):
		if not self.turn_over_time:
			self.turn_over_time = 0.0
		self.total_duration = self.duration + self.turn_over_time

	def set_item(self):
		if not self.item:

			doc= frappe.get_doc({
				"doctype": 'Item',
				"item_code": self.spa_name,
				"item_name": self.spa_name,
				"is_stock_item": 0,
				"item_group": self.spa_category,
				"stock_uom": "Nos",
				"standard_rate": self.price,
				"item_defaults":[{
					"selling_cost_center": self.cost_center,
					"income_account": self.revenue_account
				}]
			})
			# doc["item_defaults"].append ({
			# 	"selling_cost_center": self.cost_center,
			# 	"income_account": self.revenue_account
			# })
			doc.insert()
			self.item= doc.name
