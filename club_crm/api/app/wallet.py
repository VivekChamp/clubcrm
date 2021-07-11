# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt
from frappe.model.document import Document

@frappe.whitelist()
def get_balance():
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_all('Wallet Transaction', filters={'client_id': client.name, 'docstatus':1, 'transaction_type': ['in',['Top Up','Refund']]}, fields={'amount'})
    if doc:
        t = [each['amount'] for each in doc]
        topup= sum(t)
        pay= frappe.get_all('Wallet Transaction', filters={'client_id': client.name, 'transaction_type':'Payment'}, fields={'amount'})
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
def transactions():
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_all('Wallet Transaction', filters={'client_id': client.name, 'transaction_status':'Complete'}, fields={'date', 'transaction_type', 'amount','mode_of_payment','payment_type'})
    if doc:
        wallet = []
        for d in doc:
            if d.mode_of_payment==None:
                wallet.append({
                    "payment_type": d.payment_type,
                    "amount": d.amount,
                    "mode_of_payment": d.payment_type,
                    "transaction_type": d.transaction_type,
                    "date": d.date
                })
            else:
                wallet.append({
                    "payment_type": d.payment_type,
                    "amount": d.amount,
                    "mode_of_payment": d.mode_of_payment,
                    "transaction_type": d.transaction_type,
                    "date": d.date
                })

        return wallet
    # else:
    #     return 0

@frappe.whitelist()
def wallet_topup(amount):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    
    doc = frappe.get_doc({
        'doctype': 'Wallet Transaction',
        'client_id': client.name,
        'transaction_type': 'Top Up',
        'mode_of_payment': 'Online Payment',
        'transaction_date': getdate(),
        'amount': float(amount)
    })
    doc.save()
    frappe.response["message"] = {
        "status": 1,
        "wallet_name": doc.name
    }

