# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt, now_datetime
from frappe.model.document import Document

class BulkExtendValidity(Document):
	@frappe.whitelist()
	def bulk_update(self):
		today = getdate()
		if self.extend_on == "Memberships":
			mem_list = frappe.get_all("Memberships", filters={'membership_category':self.membership_category, 'expiry_date':['>', self.start_date]})
			if mem_list:
				for mem in mem_list:
					doc = frappe.get_doc('Memberships', mem.name)
					doc.append('validity_extension', {
						'entry_date': today,
						'days': self.days,
						'notes': self.notes
					})
					doc.save()
				frappe.msgprint(msg='Selected memberships has been updated.')
			else:
				frappe.msgprint(msg='No memberships found matching the criteria.')

# @frappe.whitelist()
# def bulk_update(date):
# 	mem_list = frappe.get_all("Memberships", filters={'membership_category':'Standard', 'expiry_date':['>', date]}, fields={'name', 'expiry_date'})
# 	for mem in mem_list:
# 		doc = frappe.get_doc('Memberships', mem.name)
# 		return doc