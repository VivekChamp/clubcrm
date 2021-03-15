# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date, time
from frappe.model.document import Document

class Cart(Document):
	def validate(self):
		pass
		# if self.appointments_check==1:
		# 	self.set_appointment_qty_and_total()
		# else:
		# 	self.net_total_appointments="0"
		# 	self.quantity_appointments="0"
		# if self.sessions_check==1:
		# 	self.set_session_qty_and_total()
		# else:
		# 	self.net_total_sessions="0"
		# 	self.quantity_sessions="0"
		# if self.products_check==1:
		# 	self.set_product_qty_and_total()
		# else:
		# 	self.net_total_products="0"
		# 	self.quantity_products="0"
		# # self.set_discounts_and_total()

	def set_appointment_qty_and_total(self):
		self.net_total_appointments="0"
		self.net_total_products="0"
		self.quantity_appoinments="0"
		self.quantity_products="0"

		for row in self.cart_appointment:
			self.net_total_appointments += row.total_price
			self.quantity_appointments += 1

	def set_session_qty_and_total(self):
		self.net_total_sessions="0"
		self.quantity_sessions="0"

		for row in self.cart_sessions:
			self.net_total_sessions += row.total_price
			self.quantity_sessions += 1

	def set_product_qty_and_total(self):
		self.net_total_products="0"
		self.quantity_products="0"

		for row in self.cart_product:
			self.net_total_products += row.total_price
			self.quantity_products += 1
	
	def set_discounts_and_total(self):
		self.net_total = self.net_total_appointments + self.net_total_sessions + self.net_total_products
		self.total_quantity = self.quantity_appointments + self.quantity_sessions + self.quantity_products

		if self.apply_discount=="Amount":
			self.discount_percentage = "0"
		elif self.apply_discount=="Percentage on Net Total":
			discount_amount =  (self.net_total * self.discount_percentage) / 100
			self.discount_amount = float(discount_amount//0.5*0.5)
		else:
			self.discount_percentage = "0"
			self.discount_amount = "0"
		self.grand_total = self.net_total - self.discount_amount


@frappe.whitelist(allow_guest=True)
def add_cart_from_spa(client_id, appointment_id):
	today = getdate()
	client= frappe.get_doc('Client', client_id)
	if client.membership_status=="Member":
		discount_amount="25"
	else:
		discount_amount="0"
	client_cart = frappe.get_all('Cart', filters={'client_id': client_id, 'payment_status':'Not Paid', 'date': today}, fields=["*"])
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	if not client_cart:
		doc= frappe.get_doc({
				"doctype": 'Cart',
				"client_id": client_id
			})
		doc.append('cart_appointment', {
			"appointment_type": "Spa Appointment",
			"appointment_id": appointment_id,
			"description": appointment.spa_service,
			"unit_price": appointment.default_price,
			"discount": discount_amount
		})
		if appointment.addon_table:
			for d in appointment.get('addon_table'):
				doc.append('cart_appointment', {
					"appointment_type": "Spa Appointment",
					"appointment_id": appointment_id,
					"description": d.addon_service,
					"unit_price": d.addon_price,
					"discount": discount_amount
				})
		doc.save()
		frappe.db.set_value("Spa Appointment",appointment_id,"cart", doc.name)
	else:
		cart =client_cart[0]
		cart_update = frappe.get_doc('Cart', cart.name)
		cart_update.append('cart_appointment', {
			"appointment_type": "Spa Appointment",
			"appointment_id": appointment_id,
			"description": appointment.spa_service,
			"unit_price": appointment.default_price,
			"discount": discount_amount
		})
		if appointment.addon_table:
			for d in appointment.get('addon_table'):
				cart_update.append('cart_appointment', {
			 		"appointment_type": "Spa Appointment",
					"appointment_id": appointment_id,
					"description": d.addon_service,
					"unit_price": d.addon_price,
					"discount": discount_amount
				})
		cart_update.save()
		frappe.db.set_value("Spa Appointment",appointment_id,"cart", cart.name)
	frappe.db.set_value("Spa Appointment",appointment_id,"payment_status", "Added to cart")






		
