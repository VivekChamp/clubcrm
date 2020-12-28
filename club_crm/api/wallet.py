# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt
from frappe.model.document import Document

@frappe.whitelist()
def get_balance(client_id):
    doc = frappe.get_list('Wallet Transaction', filters={'client_id':client_id, 'docstatus':1, 'transaction_type': ['in',['Top Up','Refund']]}, fields={'amount'})
    if doc:
        t = [each['amount'] for each in doc]
        topup= sum(t)
        pay= frappe.get_list('Wallet Transaction', filters={'client_id':client_id, 'transaction_type':'Payment'}, fields={'amount'})
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
def transactions(client_id):
    doc = frappe.get_list('Wallet Transaction', filters={'client_id':client_id, 'docstatus':1}, fields={'date', 'transaction_type', 'amount','mode_of_payment','payment_type'})
    if doc:
        return doc
    else:
        return 0