# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe import _
from club_crm.club_crm.utils.sms_notification import send_sms
from club_crm.club_crm.doctype.cart.cart import submit_cart
from frappe.model.document import Document

class PaymentLog(Document):
	def validate(self):
		self.set_title()

	def after_insert(self):
		self.update_payment()

	def set_title(self):
		self.title = _('{0} {1} for {2}').format(self.req_bill_to_forename, self.req_bill_to_surname, self.req_reference_number)

	def update_payment(self):
		membership_application = "^MEM-APP-[0-9]{4,4}-[0-9]{5,5}$"
		cart = "^CART-[0-9]{4,4}-[0-9]{5,5}$"
		wallet = "^WALL-[0-9]{4,4}-[0-9]{5,5}$"
		online = "^ON-[0-9]{4,4}-[0-9]{5,5}$"

		if self.decision == "ACCEPT" and self.req_amount == self.auth_amount:
			if re.match(membership_application, self.req_reference_number):
				doc = frappe.get_doc("Memberships Application", str(self.req_reference_number))
				doc.append('membership_payment', {
					"mode_of_payment": "Online Payment",
					"paid_amount": float(self.auth_amount)
				})
				doc.payment_status = 'Paid'
				doc.save(ignore_permissions=True)

				cec_list = frappe.get_all('Service Staff', filters={'display_name': doc.assigned_to})
				msg = "Payment for the membership application "+doc.name+" has been received."
				if cec_list:
					for cec in cec_list:
						receiver_list='"'+str(cec.mobile_no)+'"'
						send_sms(receiver_list,msg)
			
			if re.match(cart, self.req_reference_number):
				doc = frappe.get_doc("Cart", str(self.req_reference_number))
				doc.append('payment_table', {
					"mode_of_payment": "Online Payment",
					"paid_amount": float(self.auth_amount)
				})
				doc.save(ignore_permissions=True)
				submit_cart(doc.name)
			
			if re.match(wallet, self.req_reference_number):
				doc = frappe.get_doc("Wallet Transaction", str(self.req_reference_number))
				
				frappe.db.set_value('Wallet Transaction', self.req_reference_number, {
				'transaction_status': 'Complete',
				'transaction_reference': self.name,
				'docstatus' : 1
				})
				frappe.db.commit()
			
@frappe.whitelist()
def update_payment(docname, amount):
	doc = frappe.get_doc("Memberships Application", docname)
	doc.append('membership_payment', {
		"mode_of_payment": "Online Payment",
		"paid_amount": amount
		})
	doc.payment_status = "Paid"
	doc.save()
	frappe.db.commit()