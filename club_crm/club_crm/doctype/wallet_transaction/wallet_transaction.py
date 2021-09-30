# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
<<<<<<< HEAD
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

=======
from frappe.utils import getdate, get_time, flt, now_datetime
from frappe.model.document import Document

class WalletTransaction(Document):
    def on_submit(self):
        self.set_status()
        self.set_wallet_balance()
        
    def set_status(self):
        self.transaction_status = "Complete"
    
    def set_wallet_balance(self):
        if self.transaction_status == "Complete" and self.transaction_type == "Top Up" or self.transaction_type == "Refund":
            if self.amount:
                wallet_balance = frappe.db.get_value('Client', self.client_id, 'wallet_balance')
                new_balance = wallet_balance + self.amount
                frappe.db.set_value('Client', self.client_id, 'wallet_balance', new_balance)
                
        if self.transaction_status == "Complete" and (self.transaction_type == "Payment"):
            if self.amount:
                wallet_balance = frappe.db.get_value('Client', self.client_id, 'wallet_balance')
                new_balance = wallet_balance - self.amount
                frappe.db.set_value('Client', self.client_id, 'wallet_balance', new_balance)


@frappe.whitelist()
def get_balance_client(client_id):
    doc = frappe.get_all('Wallet Transaction', filters={'client_id': client_id, 'docstatus':1, 'transaction_type': ['in',['Top Up','Refund']]}, fields={'amount'})
    if doc:
        t = [each['amount'] for each in doc]
        topup = sum(t)
        pay = frappe.get_all('Wallet Transaction', filters={'client_id': client_id, 'transaction_type':'Payment'}, fields={'amount'})
        if pay:
            s = [each['amount'] for each in pay]
            payment=sum(s)
            wallet = topup-payment
            return wallet
        else:
            payment=0
            wallet = topup-payment
            return wallet
    else:
        return 0

@frappe.whitelist()
def remove_draft_topup():
    wallet_list = frappe.get_all('Wallet Transaction', filters={'transaction_type': 'Top Up', 'transaction_status': 'Draft', 'docstatus': 0})
    for wallets in wallet_list:
        wallet = frappe.get_doc('Wallet Transaction', wallets.name)
        wallet.delete()
>>>>>>> 7c0ae1cbc0f331aeacabc7dd76d22d6a4329518b
