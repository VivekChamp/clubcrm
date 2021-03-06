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
		self.set_item_price()
		self.set_net_price()
		self.set_discount_and_grand_total()
		self.set_payment_details()
		self.create_wallet_transaction()
		self.create_coupon_transaction()
	
	def create_wallet_transaction(self):
		# if self.payment_status == "Paid":
		for row in self.payment_table:
			if not frappe.db.get_value('Wallet Transaction', {
				'client_id': self.client_id,
				'transaction_type': 'Payment',
				'mode_of_payment': row.mode_of_payment,
				'transaction_date': getdate(),
				'amount': float(row.paid_amount),
				'transaction_document':self.name,
				'transaction_status':'Complete'
			}):
				doc = frappe.get_doc({
					'doctype': 'Wallet Transaction',
					'client_id': self.client_id,
					'transaction_type': 'Payment',
					'mode_of_payment': row.mode_of_payment,
					'transaction_date': getdate(),
					'amount': float(row.paid_amount),
					'transaction_document':self.name,
					'transaction_status':'Complete'
				})
				doc.save()
	def create_coupon_transaction(self):
		# if self.payment_status == "Paid":
		for row in self.payment_table:
			if not frappe.db.get_value('Coupon Transaction', {
				'client_id': self.client_id,
				'transaction_type': 'Payment',
				'mode_of_payment': row.mode_of_payment,
				'transaction_date': getdate(),
				'amount': float(row.paid_amount),
				'reference_doc':self.name,
				'transaction_status':'Complete'
			}):
				doc = frappe.get_doc({
					'doctype': 'Coupon Transaction',
					'client_id': self.client_id,
					'transaction_type': 'Payment',
					'mode_of_payment': row.mode_of_payment,
					'transaction_date': getdate(),
					'amount': float(row.paid_amount),
					'reference_doc':self.name,
					'transaction_status':'Complete'
				})
				doc.save()

	def on_trash(self):
		if self.payment_status=="Paid":
			frappe.throw(msg="Paid cart cannot be cancelled", title=_('Not Allowed'))
		else:
			spa_list = frappe.get_all('Spa Appointment', filters={'cart': self.name})
			if spa_list:
				for spa in spa_list:
					frappe.db.set_value("Spa Appointment", spa.name, "cart", None)

	def set_item_price(self):
		if self.products_check==1:
			if self.cart_product:
				for row in self.cart_product:
					prices = frappe.get_all('Item Price', filters={'item_code':row.cart_item, 'price_list':'Standard Selling'}, fields=['*'])
					if prices:
						for price in prices:
							row.unit_price = price.price_list_rate

	def set_net_price(self):
		self.net_total_appointments = 0.0
		self.net_total_sessions = 0.0
		self.net_total_products = 0.0
		self.total_tips = 0.0
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
				item_price = float(row.unit_price) - (float(row.unit_price) * float(row.discount)/100.0)
				price = float(item_price)//0.5*0.5
				row.total_price = float(price) * float(row.qty)
				self.quantity_products += int(row.qty)
				self.net_total_products += row.total_price
		
		if self.tips_check ==1:
			for row in self.cart_tips:
				self.total_tips += row.tips_amount
		
		self.net_total = self.net_total_appointments + self.net_total_sessions + self.net_total_products + self.total_tips
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
			if row.package_type == "Club":
				service_type = "Club Services"
			club_package = frappe.get_doc('Club Packages', row.package_name)
			if club_package.package_table:
				for item in club_package.package_table:
					create_session(self.client_id,row.package_name,service_type,item.service_name,item.no_of_sessions,item.validity)

	def make_paid(self):
		for row in self.cart_appointment:
			if row.appointment_type == "Spa Appointment":
				doc = frappe.get_doc('Spa Appointment', row.appointment_id)
				doc.payment_status = 'Paid'
				doc.save()
				# frappe.db.set_value('Spa Appointment', row.appointment_id, 'payment_status', 'Paid')
				frappe.db.commit()
			if row.appointment_type == "Fitness Training Appointment":
				frappe.db.set_value('Fitness Training Appointment', row.appointment_id, 'payment_status', 'Paid')
				frappe.db.commit()

@frappe.whitelist()
def add_cart_from_spa(client_id, appointment_id):
	today = getdate()
	discount_amount = 0.0
	client = frappe.get_doc('Client', client_id)
	if client.membership_status=="Member":
		if client.membership_history:
			for row in client.membership_history:
				if row.status == "Active":
					mem = frappe.get_doc('Memberships', row.membership)
					discount_amount = mem.spa_discount

	client_cart = frappe.get_all('Cart', filters={'client_id': client_id, 'payment_status':'Not Paid', 'date': today}, fields=["*"])
	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	spa = frappe.get_doc('Spa Services', appointment.spa_service)
	if spa.no_member_discount == 1:
            discount_amount = 0.0
	
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
		frappe.db.set_value("Spa Appointment",appointment_id,"payment_status", "Added to cart")
		return doc.name
	else:
		cart = client_cart[0]
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
		return cart.name

@frappe.whitelist()
def remove_cart_from_spa(cart_id, appointment_id):
	cart = frappe.get_doc('Cart', cart_id)
	if cart.cart_appointment:
		for row in cart.cart_appointment:
			if appointment_id == row.appointment_id:
				cart.remove(row)
		
	if not cart.cart_appointmnent:
		cart.payment_status = "Cancelled"
		cart.save()

	frappe.db.set_value("Spa Appointment",appointment_id,"cart", "")
	frappe.db.set_value("Spa Appointment",appointment_id,"payment_status", "Not Paid")

	frappe.msgprint(msg="Removed from Cart", title='Success')

@frappe.whitelist()
def add_cart_from_fitness(client_id, appointment_id):
	discount_amount= 0.0
	today = getdate()
	client= frappe.get_doc('Client', client_id)
	# if client.membership_status=="Member":
	# 	discount_amount="25.0"
	# else:
	# 	discount_amount="0.0"
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

@frappe.whitelist()
def add_cart_from_spa_online(client_id, appointment_id):
	discount_amount = 0.0
	client = frappe.get_doc('Client', client_id)
	if client.membership_status == "Member":
		if client.membership_history:
			for row in client.membership_history:
				if row.status == "Active":
					mem = frappe.get_doc('Memberships', row.membership)
					discount_amount = mem.spa_discount

	appointment = frappe.get_doc('Spa Appointment', appointment_id)
	
	spa = frappe.get_doc('Spa Services', appointment.spa_service)
	if spa.no_member_discount == 1:
            discount_amount = 0.0

	doc= frappe.get_doc({
		"doctype": 'Cart',
		'online': 1,
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
	doc.save()
	frappe.db.set_value("Spa Appointment",appointment_id,"cart", doc.name)
	
	if appointment.payment_method == "Wallet":
		wallet = frappe.get_doc({
        	'doctype': 'Wallet Transaction',
        	'client_id': client_id,
        	'transaction_type': 'Payment',
			'payment_type': 'Cart',
			'transaction_document': doc.name,
        	'transaction_date': getdate(),
        	'amount': doc.grand_total
    	})
		wallet.save()
		wallet.submit()
		doc.append('payment_table', {
			"mode_of_payment": "Wallet",
			"paid_amount": doc.grand_total
		})
		doc.save(ignore_permissions=True)
		submit_cart(doc.name)

	return doc.name

# Submit cart and create sales invoice
@frappe.whitelist()
def submit_cart(cart_id):
	today = getdate()
	user = frappe.get_doc('User',frappe.session.user)
	cart = frappe.get_doc('Cart', cart_id)
	if cart.balance_amount != 0.0:
		frappe.throw("The Payment is not complete.")
	else:
		cart.payment_status = "Paid"

		if cart.payment_table:
			for row in cart.payment_table:
				if row.mode_of_payment == "Wallet":
						doc = frappe.get_doc({
							'doctype': 'Wallet Transaction',
							'client_id': cart.client_id,
							'transaction_type': 'Payment',
							'transaction_date': getdate(),
							'amount': float(row.paid_amount),
							'payment_type' : 'Cart',
							'transaction_document': cart.name
						})
						doc.save()
						doc.submit()

		if cart.cart_appointment:
			for row in cart.cart_appointment:
				if row.appointment_type == "Spa Appointment":
					doc = frappe.get_doc('Spa Appointment', row.appointment_id)
					doc.cart = cart_id
					doc.payment_date = today
					doc.paid_amount = row.total_price
					doc.cart_amount = cart.grand_total
					doc.paid_by = cart.client_id
					if not user.full_name == "Administrator":
						doc.billing_staff = user.full_name
					doc.payment_status = 'Paid'
					doc.save()

				if row.appointment_type == "Fitness Training Appointment":
					frappe.db.set_value('Fitness Training Appointment', row.appointment_id, 'payment_status', 'Paid')
					frappe.db.commit()

		if cart.cart_session:
			for row in cart.cart_session:
				if row.package_type == "Spa":
					service_type = "Spa Services"
				if row.package_type == "Fitness":
					service_type = "Fitness Services"
				if row.package_type == "Club":
					service_type = "Club Services"
				club_package = frappe.get_doc('Club Packages', row.package_name)
				if club_package.package_table:
					for item in club_package.package_table:
						create_session(cart.client_id,row.package_name,service_type,item.service_name,item.no_of_sessions,item.validity)
		
		if cart.cart_product:
			if cart.online==1:
				online = frappe.get_all('Online Order', filters={'cart_id':cart_id})
				if online:
					for order in online:
						online_cart = frappe.get_doc('Online Order', order.name)
						online_cart.cart_status = "Ordered"
						online_cart.payment_status = "Paid"
						online_cart.save()

		cart.save()
		frappe.msgprint(msg='Cart has been submitted successfully')

@frappe.whitelist()
def add_cart_from_shop_online(client_id, order_id):
	online = frappe.get_doc('Online Order', order_id)
	doc= frappe.get_doc({
		"doctype": 'Cart',
		'online':1,
		"products_check": 1,
		"client_id": client_id
	})
	if online.item:
		for row in online.item:
			doc.append('cart_product', {
				"cart_item": row.item_code,
				"qty": row.quantity,
				"unit_price": row.rate,
				"discount": row.discount,
				"total_price": row.amount
			})
	doc.save()
	frappe.db.set_value('Online Order', order_id, 'cart_id', doc.name)
	frappe.db.commit()
	return doc

@frappe.whitelist()
def add_cart_from_pt_online(client_id, request_id):
	pt_request = frappe.get_doc('Fitness Training Request', request_id)
	client = frappe.get_doc('Client', client_id)

	doc= frappe.get_doc({
		"doctype": 'Cart',
		'online': 1,
		"sessions_check": 1,
		"client_id": client_id
	})
	doc.append('cart_session', {
		"package_type": "Fitness",
		"package_name": pt_request.fitness_package,
		"unit_price": pt_request.price,
		"total_price": pt_request.price
	})
	doc.save()
	return doc

# Create Payment Entry for paid carts
@frappe.whitelist()
def create_payment_entry():
	today = getdate()

	cart_list = frappe.get_all('Cart', filters={'date': today, 'payment_status': 'Paid', 'payment_entry': 0})
	if cart_list:
		for carts in cart_list:
			cart = frappe.get_doc('Cart', carts.name)

			if cart.payment_status=="Paid":
				if cart.payment_table:
					for row in cart.payment_table:
						pe = frappe.new_doc('Payment Entry')
						pe.posting_date = row.payment_date
						pe.payment_type = "Receive"
						pe.mode_of_payment = row.mode_of_payment
						pe.party_type = "Customer"
						pe.party = frappe.get_value('Client', cart.client_id, 'customer')
						pe.paid_to_account_currency = 'QAR'
						pe.paid_to = get_paid_to_account(row.mode_of_payment)
						pe.paid_amount = row.paid_amount
						pe.received_amount = row.paid_amount
						pe.target_exchange_rate = 1
						pe.reference_no = row.transaction_reference
						pe.reference_date = row.payment_date
						pe.insert(ignore_permissions=True)
						pe.submit()

					frappe.db.set_value('Cart', cart.name, 'payment_entry', 1)
					frappe.db.set_value('Cart', cart.name, 'docstatus', 1)


#  Fetch accounts for mode of payment
@frappe.whitelist()
def get_paid_to_account(mode_of_payment):
	mop = frappe.get_doc('Mode of Payment', mode_of_payment)
	if not mop.accounts:
		frappe.throw('Please set default account for this mode of payment')
	else:
		for row in mop.accounts:
			account = row.default_account
			
			return account

# Fetch items in Cart Products for item groups which has retail sale enabled
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_products(doctype, txt, searchfield, start, page_len, filters):
	items_list = []
	item_group = frappe.get_all('Item Group', filters={'is_retail': 1, 'is_group': 0})
	if item_group:
		for items in item_group:
			item_list = frappe.get_all("Item", filters={'item_group': items.name}, fields={'name', 'item_name', 'item_group'})
			if item_list:
				for a in item_list:
					items_list.append([
						a.item_name, a.item_group
					])
	
	return items_list
