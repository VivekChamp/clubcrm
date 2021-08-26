# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class WalletTransaction(Document):
	def validate(self):
		self.set_wallet_balance()

	def set_wallet_balance(self):
		if self.transaction_status == "Complete" and self.transaction_type == "Top Up":
			if self.amount:
				wallet_balance = frappe.db.get_value('Client', self.client_id, 'wallet_balance')
				frappe.db.set_value('Client', self.client_id, 'wallet_balance', wallet_balance+self.amount)
		if self.transaction_status == "Complete" and (self.transaction_type == "Payment" or self.transaction_type == "Refund"):
			if self.amount:
				wallet_balance = frappe.db.get_value('Client', self.client_id, 'wallet_balance')
				frappe.db.set_value('Client', self.client_id, 'wallet_balance', wallet_balance-self.amount)

