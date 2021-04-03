# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FoodOrderEntry(Document):
	def validate(self):
		self.set_price()
		self.set_total_and_quantity()

	def set_price(self):
		if self.order_items:
			for row in self.order_items:
				row.rate = 0.0
				item_price = frappe.get_all('Item Price', filters={'item_code' : row.item, 'price_list': 'Grams Menu'}, fields=['name','item_code','price_list_rate'])
				for item in item_price:
					row.rate = item.price_list_rate

	def set_total_and_quantity(self):
		self.total_quantity = 0
		self.total_amount = 0.0

		if self.order_items:
			for row in self.order_items:
				row.amount = float(row.rate) * float(row.qty)
				self.total_quantity += int(row.qty)
				self.total_amount += row.amount
	

