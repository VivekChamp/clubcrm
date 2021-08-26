# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, get_time, flt
class ClubCoupon(Document):
	def validate(self):
		self.create_coupon_transaction()

	def create_coupon_transaction(self):
		if self.payment_status == "Paid":
			if not frappe.db.get_value('Coupon Transaction', {
				'client_id': self.client,
				'transaction_type': 'New Coupon',
				# 'mode_of_payment': self.mode_of_payment,
				'transaction_date': getdate(),
				'amount': float(self.price),
				# 'reference_doc':self.name,
				'transaction_status':'Complete'
			}):
				doc = frappe.get_doc({
					'doctype': 'Coupon Transaction',
					'client_id': self.client,
					'transaction_type': 'New Coupon',
					# 'mode_of_payment': row.mode_of_payment,
					'transaction_date': getdate(),
					'amount': float(self.price),
					# 'reference_doc':self.name,
					'transaction_status':'Complete'
				})
				doc.save()
