# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CouponTransaction(Document):
	def validate(self):
		self.set_coupon_amount()

	def set_coupon_amount(self):
		if self.transaction_status == "Complete" and self.transaction_type == "New Coupon":
			if self.amount:
				coupon_amount = frappe.db.get_value('Client', self.client_id, 'coupon_amount')
				frappe.db.set_value('Client', self.client_id, 'coupon_amount', coupon_amount+self.amount)
		if self.transaction_status == "Complete" and (self.transaction_type == "Payment" or self.transaction_type == "Refund"):
			if self.amount:
				coupon_amount = frappe.db.get_value('Client', self.client_id, 'coupon_amount')
				frappe.db.set_value('Client', self.client_id, 'coupon_amount', coupon_amount-self.amount)


