# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SpaServicesCategory(Document):
	def validate(self):
		self.set_item_group()

	def set_item_group(self):
		if not self.item_category:
			doc= frappe.get_doc({
				"doctype": 'Item Group',
				"item_group_name": self.spa_category_name,
				"parent_item_group": 'Treatments'
			})
			doc.insert()
			self.item_category= doc.name
		
		# else:
		# 	item_group= frappe.get_doc('Item Group', self.item_category)
		# 	if item_group:
		# 		item_group.name=self.spa_category_name
		# 		item_group.item_group_name=self.spa_category_name
		# 		item_group.save()
		# 		self.item_category=item_group.name





    
