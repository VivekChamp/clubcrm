# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from club_crm.club_crm.utils.sms_notification import send_sms
from club_crm.club_crm.utils.push_notification import send_push
from frappe.model.document import Document

class FoodOrderEntry(Document):
	def validate(self):
		self.set_price()
		self.set_total_and_quantity()
		self.send_notifications()

	def set_price(self):
		if self.order_items:
			for row in self.order_items:
				row.rate = 0.0
				item_price = frappe.get_all('Item Price', filters={'item_code' : row.item, 'price_list': 'Grams Menu'}, fields=['name','item_code','price_list_rate'])
				for item in item_price:
					row.rate = item.price_list_rate

	def set_total_and_quantity(self):
		self.total_quantity = 0
		self.total_amount = 0.0
		self.total_to_be_paid = 0.0
		self.paid_amount = 0.0
		self.balance_amount = 0.0

		if self.order_items:
			for row in self.order_items:
				row.amount = float(row.rate) * float(row.qty)
				self.total_quantity += int(row.qty)
				self.total_amount += row.amount
		
		self.total_to_be_paid = self.total_amount

		if self.payment_table:
			for row in self.payment_table:
				self.paid_amount += row.paid_amount
		self.balance_amount = self.total_to_be_paid - self.paid_amount
		if self.balance_amount == 0.0:
			frappe.db.set_value("Food Order Entry", self.name, "payment_status", "Paid")

	def send_notifications(self):
		if self.order_notify_client==0 and self.order_status=="Ordered":
			client = frappe.get_doc('Client', self.client_id)
			msg = "Thank you for placing the order with Grams. We will notify you once your order is ready."
			receiver_list='"'+str(self.mobile_number)+'"'
			send_sms(receiver_list,msg)

			if client.fcm_token:
				title = "Grams at Katara Club"
				send_push(client.name,title,msg)
			self.order_notify_client=1

		if self.ready_notify==0 and self.order_status=="Ready":
			client = frappe.get_doc('Client', self.client_id)
			msg = "Your food order from Grams is ready."
			receiver_list='"'+str(self.mobile_number)+'"'
			send_sms(receiver_list,msg)

			if client.fcm_token:
				title = "Grams at Katara Club"
				send_push(client.name,title,msg)
			self.ready_notify=1