# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe import _
from frappe.utils import getdate, get_time, flt, now_datetime
from club_crm.club_crm.utils.sms_notification import send_sms
from club_crm.club_crm.doctype.cart.cart import submit_cart
from frappe.model.document import Document

class PaymentLog(Document):
	def validate(self):
		self.set_title()
		self.get_client_id()
		self.set_doctype()

	def set_title(self):
		if self.req_transaction_type == "sale":
			self.title = _('{0} {1} for {2}').format(self.req_bill_to_forename, self.req_bill_to_surname, self.req_reference_number)
		elif self.req_transaction_type == "create_payment_token":
			self.title = _('Save card by {0} {1}').format(self.req_bill_to_forename, self.req_bill_to_surname)

	def get_client_id(self):
		client = frappe.db.get("Client", {"email": self.req_bill_to_email})
		if client:
			self.client_id = client.name

	def set_doctype(self):
		membership_application = "^MEM-APP-[0-9]{4,4}-[0-9]{5,5}$"
		cart = "^CART-[0-9]{4,4}-[0-9]{5,5}$"
		wallet = "^WALL-[0-9]{4,4}-[0-9]{5,5}$"
		food = "^FOE-[0-9]{4,4}-[0-9]{5,5}$"
		fitness = "^FIT-REQ-[0-9]{4,4}-[0-9]{5,5}$"

		if not self.req_transaction_type == "create_payment_token":
			if re.match(membership_application, self.req_reference_number):
				self.document_type = "Memberships Application"
				self.reference_doc = self.req_reference_number
			elif re.match(cart, self.req_reference_number):
				self.document_type = "Cart"
				self.reference_doc = self.req_reference_number
			elif re.match(wallet, self.req_reference_number):
				self.document_type = "Wallet Transaction"
				self.reference_doc = self.req_reference_number
			elif re.match(food, self.req_reference_number):
				self.document_type = "Food Order Entry"
				self.reference_doc = self.req_reference_number
			elif re.match(fitness, self.req_reference_number):
				self.document_type = "Fitness Training Request"
				self.reference_doc = self.req_reference_number


# Cron job action to update payments 
@frappe.whitelist()
def update_payments():
	today = getdate()
	membership_application = "^MEM-APP-[0-9]{4,4}-[0-9]{5,5}$"
	cart = "^CART-[0-9]{4,4}-[0-9]{5,5}$"
	wallet = "^WALL-[0-9]{4,4}-[0-9]{5,5}$"
	food = "^FOE-[0-9]{4,4}-[0-9]{5,5}$"
	fitness = "^FIT-REQ-[0-9]{4,4}-[0-9]{5,5}$"

	payment_list = frappe.get_all('Payment Log', filters={'date_time': today, 'payment_updated': 0})
	for payment in payment_list:
		payment_log = frappe.get_doc('Payment Log', payment.name)
		
		if payment_log.req_transaction_type == "sale":
			if payment_log.decision == "ACCEPT" and payment_log.req_amount == payment_log.auth_amount:
				if re.match(membership_application, payment_log.req_reference_number):
					doc = frappe.get_doc("Memberships Application", str(payment_log.req_reference_number))
					doc.append('membership_payment', {
						"payment_date": getdate(),
						"mode_of_payment": "Online Payment",
						"paid_amount": float(payment_log.auth_amount)
					})
					doc.payment_status = 'Paid'
					doc.save(ignore_permissions=True)

					if doc.assigned_to and doc.cec_mobile_no:
						msg = "Payment for the membership application "+doc.name+" has been received."
						receiver_list='"'+str(doc.cec_mobile_no)+'"'
						send_sms(receiver_list,msg)
				
				if re.match(cart, payment_log.req_reference_number):
					doc = frappe.get_doc("Cart", str(payment_log.req_reference_number))
					doc.append('payment_table', {
						"payment_date": getdate(),
						"mode_of_payment": "Online Payment",
						"paid_amount": float(payment_log.auth_amount)
					})
					doc.save(ignore_permissions=True)
					submit_cart(doc.name)
				
				if re.match(wallet, payment_log.req_reference_number):
					doc = frappe.get_doc("Wallet Transaction", str(payment_log.req_reference_number))
					
					frappe.db.set_value('Wallet Transaction', payment_log.req_reference_number, {
					'transaction_status': 'Complete',
					'transaction_reference': payment_log.name,
					'docstatus' : 1
					})
					frappe.db.commit()

				if re.match(food, payment_log.req_reference_number):
					doc = frappe.get_doc("Food Order Entry", str(payment_log.req_reference_number))
					doc.append('payment_table', {
						"payment_date": getdate(),
						"mode_of_payment": "Online Payment",
						"paid_amount": float(payment_log.auth_amount)
					})
					doc.order_status = "Ordered"
					doc.payment_status = "Paid"
					doc.save(ignore_permissions=True)

				if re.match(fitness, payment_log.req_reference_number):
					doc = frappe.get_doc("Fitness Training Request", str(payment_log.req_reference_number))
					doc.append('payment_table', {
						"payment_date": getdate(),
						"mode_of_payment": "Online Payment",
						"paid_amount": float(payment_log.auth_amount)
					})
					doc.request_status = "Completed"
					doc.payment_status = "Paid"
					doc.save(ignore_permissions=True)
				
			frappe.db.set_value('Payment Log', payment_log.name, 'payment_updated', 1)
			frappe.db.commit()
		
		elif payment_log.req_transaction_type == "create_payment_token":
			doc = frappe.get_doc({
				'doctype': 'Card Token',
				'client_id': payment_log.client_id,
				'card_type' : payment_log.card_type_name,
				'last_4_digits_of_card': payment_log.req_card_number,
				'card_expiry_date' : payment_log.req_card_expiry_date,
				'payment_token': payment_log.req_payment_token
			})
			doc.save()
			frappe.db.set_value('Payment Log', payment_log.name, 'payment_updated', 1)
			frappe.db.commit()

# Manual updation of payment in case of payment failures
@frappe.whitelist()
def update_payment_manual(doc_id):
	membership_application = "^MEM-APP-[0-9]{4,4}-[0-9]{5,5}$"
	cart = "^CART-[0-9]{4,4}-[0-9]{5,5}$"
	wallet = "^WALL-[0-9]{4,4}-[0-9]{5,5}$"
	food = "^FOE-[0-9]{4,4}-[0-9]{5,5}$"
	fitness = "^FIT-REQ-[0-9]{4,4}-[0-9]{5,5}$"
	# online = "^ON-[0-9]{4,4}-[0-9]{5,5}$"

	payment_log = frappe.get_doc('Payment Log', doc_id)
		
	if payment_log.decision == "ACCEPT" and payment_log.req_amount == payment_log.auth_amount:
		if re.match(membership_application, payment_log.req_reference_number):
			doc = frappe.get_doc("Memberships Application", str(payment_log.req_reference_number))
			doc.append('membership_payment', {
				"payment_date": getdate(),
				"mode_of_payment": "Online Payment",
				"paid_amount": float(payment_log.auth_amount)
			})
			doc.payment_status = 'Paid'
			doc.save(ignore_permissions=True)

			if doc.assigned_to and doc.cec_mobile_no:
				msg = "Payment for the membership application "+doc.name+" has been received."
				receiver_list='"'+str(doc.cec_mobile_no)+'"'
				send_sms(receiver_list,msg)
			
		if re.match(cart, payment_log.req_reference_number):
			doc = frappe.get_doc("Cart", str(payment_log.req_reference_number))
			doc.append('payment_table', {
				"payment_date": getdate(),
				"mode_of_payment": "Online Payment",
				"paid_amount": float(payment_log.auth_amount)
			})
			doc.save(ignore_permissions=True)
			submit_cart(doc.name)
			
		if re.match(wallet, payment_log.req_reference_number):
			doc = frappe.get_doc("Wallet Transaction", str(payment_log.req_reference_number))
				
			frappe.db.set_value('Wallet Transaction', payment_log.req_reference_number, {
				'transaction_status': 'Complete',
				'transaction_reference': payment_log.name,
				'docstatus' : 1
			})
			frappe.db.commit()

		if re.match(food, payment_log.req_reference_number):
			doc = frappe.get_doc("Food Order Entry", str(payment_log.req_reference_number))
			doc.append('payment_table', {
				"payment_date": getdate(),
				"mode_of_payment": "Online Payment",
				"paid_amount": float(payment_log.auth_amount)
			})
			doc.order_status = "Ordered"
			doc.payment_status = "Paid"
			doc.save(ignore_permissions=True)

		if re.match(fitness, payment_log.req_reference_number):
			doc = frappe.get_doc("Fitness Training Request", str(payment_log.req_reference_number))
			doc.append('payment_table', {
				"payment_date": getdate(),
				"mode_of_payment": "Online Payment",
				"paid_amount": float(payment_log.auth_amount)
			})
			doc.request_status = "Completed"
			doc.payment_status = "Paid"
			doc.save(ignore_permissions=True)
			
	frappe.db.set_value('Payment Log', payment_log.name, 'payment_updated', 1)
	frappe.db.commit()
	frappe.msgprint(msg = "Payment has been updated", title="Success")