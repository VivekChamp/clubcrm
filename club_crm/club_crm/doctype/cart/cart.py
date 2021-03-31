# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date, time
from club_crm.club_crm.doctype.client_sessions.client_sessions import create_session
from frappe.model.document import Document

class Cart(Document):
	def validate(self):
		self.set_net_price()
		self.set_discount_and_grand_total()
		self.set_payment_details()

	def before_submit(self):
		self.check_payment()
		self.set_status()

	def on_submit(self):
		if self.cart_appointment:
			self.make_paid()
		if self.cart_session:
			self.create_session()

	def set_net_price(self):
		self.net_total_appointments = 0.0
		self.net_total_sessions = 0.0
		self.net_total_products = 0.0
		self.quantity_appointments = 0
		self.quantity_sessions = 0
		self.quantity_products = 0

		if self.appointments_check==1:
			for row in self.cart_appointment:
				row.total_price = float(row.unit_price) - (float(row.unit_price) * float(row.discount)/100)
				self.quantity_appointments += 1
				self.net_total_appointments += row.total_price

		if self.sessions_check==1:
			for row in self.cart_session:
				row.total_price = float(row.unit_price) - (float(row.unit_price) * float(row.discount)/100)
				self.quantity_sessions += 1
				self.net_total_sessions += row.total_price

		if self.products_check==1:
			for row in self.cart_product:
				p_total = float(row.qty) * row.unit_price
				row.total_price = float(p_total) - (float(p_total) * float(row.discount)/100)
				self.quantity_products += 1
				self.net_total_products += row.total_price
		
		self.net_total = self.net_total_appointments + self.net_total_sessions + self.net_total_products
		self.total_quantity = self.quantity_appointments + self.quantity_sessions + self.quantity_products

	def set_discount_and_grand_total(self):
		if self.apply_discount=="Amount":
			self.discount_percentage = 0.0
		elif self.apply_discount=="Percentage on Net Total":
			discount_amount =  (self.net_total * self.discount_percentage) / 100
			self.discount_amount = float(discount_amount//0.5*0.5)
		else:
			self.discount_percentage = 0.0
			self.discount_amount = 0.0
		self.grand_total = self.net_total - self.discount_amount

	def set_payment_details(self):
		self.paid_amount = 0.0
		self.total_to_be_paid = self.grand_total
		if self.payment_table:
			for row in self.payment_table:
				self.paid_amount += row.paid_amount
		self.balance_amount = self.total_to_be_paid - self.paid_amount
		if self.balance_amount == 0.0:
			frappe.db.set_value("Cart", self.name, "payment_status", "Paid")
		
	def check_payment(self):
		if self.balance_amount != 0.0:
			frappe.throw("The Payment is not complete.")

	def set_status(self):
		self.payment_status = "Paid"

	def create_session(self):
		for row in self.cart_session:
			if row.package_type == "Spa":
				service_type = "Spa Services"
			if row.package_type == "Fitness":
				service_type = "Fitness Services"
			club_package = frappe.get_doc('Club Packages', row.package_name)
			if club_package.package_table:
				for item in club_package.package_table:
					create_session(self.client_id,row.package_name,service_type,item.service_name,item.no_of_sessions,item.validity)

	def make_paid(self):
		for row in self.cart_appointment:
			if row.appointment_type == "Spa Appointment":
				frappe.db.set_value('Spa Appointment', row.appointment_id, 'payment_status', 'Paid')
				frappe.db.commit()
			if row.appointment_type == "Fitness Training Appointment":
				frappe.db.set_value('Fitness Training Appointment', row.appointment_id, 'payment_status', 'Paid')
				frappe.db.commit()

@frappe.whitelist()
def add_cart_from_spa(client_id, appointment_id):
	today = getdate()
	client= frappe.get_doc('Client', client_id)
	if client.membership_status=="Member":
		discount_amount="25.0"
	else:
		discount_amount="0.0"
	client_cart = frappe.get_all('Cart', filters={'client_id': client_id, 'payment_status':'Not Paid', 'date': today}, fields=["*"])
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	if not client_cart:
		doc= frappe.get_doc({
				"doctype": 'Cart',
				"appointments_check": 1,
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

@frappe.whitelist()
def add_cart_from_fitness(client_id, appointment_id):
	today = getdate()
	client= frappe.get_doc('Client', client_id)
	if client.membership_status=="Member":
		discount_amount="25.0"
	else:
		discount_amount="0.0"
	client_cart = frappe.get_all('Cart', filters={'client_id': client_id, 'payment_status':'Not Paid', 'date': today}, fields=["*"])
	appointment = frappe.get_doc('Fitness Training Appointment', appointment_id)
	if not client_cart:
		doc= frappe.get_doc({
				"doctype": 'Cart',
				"appointments_check": 1,
				"client_id": client_id
			})
		doc.append('cart_appointment', {
			"appointment_type": "Fitness Training Appointment",
			"appointment_id": appointment_id,
			"description": appointment.fitness_service,
			"unit_price": appointment.default_price,
			"discount": discount_amount
		})
		doc.save()
		frappe.db.set_value("Fitness Training Appointment",appointment_id,"cart", doc.name)
	else:
		cart =client_cart[0]
		cart_update = frappe.get_doc('Cart', cart.name)
		cart_update.append('cart_appointment', {
			"appointment_type": "Fitness Training Appointment",
			"appointment_id": appointment_id,
			"description": appointment.fitness_service,
			"unit_price": appointment.default_price,
			"discount": discount_amount
		})
		cart_update.save()
		frappe.db.set_value("Fitness Training Appointment",appointment_id,"cart", cart.name)
	frappe.db.set_value("Fitness Training Appointment",appointment_id,"payment_status", "Added to cart")