# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta
from frappe.model.document import Document

class MembershipsApplication(Document):
	def before_insert(self):
		self.check_existing_application()

	def validate(self):
		self.check_clients()
		self.check_birthdate()
		self.set_pricing()
		self.set_discounts_and_grand_total()
		self.set_payment_details()
		self.set_title()
	
	def before_submit(self):
		self.check_payment()

	def on_submit(self):
		self.create_clients()

	def check_existing_application(self):
		mem_app = frappe.get_all('Memberships Application', filters={'qatar_id_1':self.qatar_id_1,'application_status':"Pending"})
		if mem_app:
			frappe.throw('A pending application already exists for this client. Kindly wait until it is reviewed.')

	def check_payment(self):
		if self.balance_amount != 0.0:
			frappe.throw("The payments for this membership is not complete. Kindly try again after completing the payments.")

	def check_clients(self):
		client_all = frappe.get_all('Client', filters={'mobile_no':self.mobile_no_1})
		if client_all:
			for client in client_all:
				self.client_id = client.name
				self.existing_client_1 = 1
		
		if self.mobile_no_2:
			client_all = frappe.get_all('Client', filters={'mobile_no':self.mobile_no_2})
			if client_all:
				for client in client_all:
					self.client_id_2 = client.name
					self.existing_client_2 = 1
		
		if self.additional_members:
			for row in self.additional_members:
				client_all = frappe.get_all('Client', filters={'mobile_no':row.mobile_no})
				if client_all:
					for client in client_all:
						row.client_id = client.name
						self.existing_client = 1
	
	def check_birthdate(self):
		today = getdate()
		self.no_of_adults = 0
		self.no_of_children = 0
		if self.birth_date_1:
			self.no_of_adults += 1

		if self.birth_date_2:
			self.no_of_adults += 1

		if self.additional_members:
			for row in self.additional_members:
				if type(row.birth_date) == str:
					dob = datetime.strptime(row.birth_date, "%Y-%m-%d")
				else:
					dob = row.birth_date
				age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
				if age >= 18:
					self.no_of_adults += 1
					row.category = "Adult"
				else:
					self.no_of_children += 1
					row.category = "Child"
	
	def set_pricing(self):
		mem_plan = frappe.get_doc('Memberships Plan', self.membership_plan)
		if self.application_type == "New":
			self.joining_fee = mem_plan.joining_fee_adult * float(self.no_of_adults)
		self.membership_fee_adult = mem_plan.membership_fee_adult * float(self.no_of_adults)
		if self.no_of_children == 1 and self.no_of_adults == 2:
			self.membership_fee_child = mem_plan.membership_fee_child * 2
		else:
			self.membership_fee_child = mem_plan.membership_fee_child * float(self.no_of_children)

		self.total_membership_fee = self.membership_fee_adult + self.membership_fee_child
		self.net_total = self.joining_fee + self.total_membership_fee

	def set_discounts_and_grand_total(self):
		self.grand_total = 0.0
		if self.discount_type == "Percentage":
			if self.apply_discount == "On Joining Fee":
				discount_amount =  (self.joining_fee * self.discount_percentage) / 100
				self.discount_amount = float(discount_amount//0.5*0.5)
			elif self.apply_discount == "On Membership Fee (Adult)":
				discount_amount =  (self.membership_fee_adult * self.discount_percentage) / 100
				self.discount_amount = float(discount_amount//0.5*0.5)
			elif self.apply_discount == "On Membership Fee (Child)":
				discount_amount =  (self.membership_fee_child * self.discount_percentage) / 100
				self.discount_amount = float(discount_amount//0.5*0.5)
			elif self.apply_discount == "On Total Membership Fee":
				discount_amount =  (self.total_membership_fee * self.discount_percentage) / 100
				self.discount_amount = float(discount_amount//0.5*0.5)
			elif self.apply_discount == "On Net Total":
				discount_amount =  (self.net_total * self.discount_percentage) / 100
				self.discount_amount = float(discount_amount//0.5*0.5)

		self.grand_total = self.net_total - self.discount_amount 

	def set_payment_details(self):
		self.paid_amount = 0.0
		self.total_to_be_paid = self.grand_total
		if self.membership_payment:
			for row in self.membership_payment:
				self.paid_amount += row.paid_amount
		self.balance_amount = self.total_to_be_paid - self.paid_amount
		if int(self.balance_amount) == 0:
			frappe.db.set_value("Memberships Application", self.name, "payment_status", "Paid")
			frappe.db.commit()

	def set_title(self):
		self.title = _('{0} for {1}').format(self.first_name_1,self.membership_plan)

	def create_clients(self):
		if self.membership_type == "Single Membership":
			if not self.client_id:
				client_1 = create_client(self.first_name_1,self.last_name_1,self.gender_1,self.birth_date_1,self.qatar_id_1,self.mobile_no_1,self.email_1)
				frappe.db.set_value("Memberships Application", self.name, "client_id", client_1, update_modified=False)
				# self.client_id = client_1

		if self.membership_type == "Couple Membership":
			if not self.client_id:
				client_1 = create_client(self.first_name_1,self.last_name_1,self.gender_1,self.birth_date_1,self.qatar_id_1,self.mobile_no_1,self.email_1)
				frappe.db.set_value("Memberships Application", self.name, "client_id", client_1, update_modified=False)
				# self.client_id = client_1

			if not self.client_id_2:
				client_2 = create_client(self.first_name_2,self.last_name_2,self.gender_2,self.birth_date_2,self.qatar_id_2,self.mobile_no_2,self.email_2)
				frappe.db.set_value("Memberships Application", self.name, "client_id_2", client_2, update_modified=False)
				# self.client_id_2 = client_2

		if self.membership_type == "Family Membership":
			if not self.client_id:
				client_1 = create_client(self.first_name_1,self.last_name_1,self.gender_1,self.birth_date_1,self.qatar_id_1,self.mobile_no_1,self.email_1)
				frappe.db.set_value("Memberships Application", self.name, "client_id", client_1, update_modified=False)
				# self.client_id = client_1

			if not self.client_id_2:
				client_2 = create_client(self.first_name_2,self.last_name_2,self.gender_2,self.birth_date_2,self.qatar_id_2,self.mobile_no_2,self.email_2)
				frappe.db.set_value("Memberships Application", self.name, "client_id_2", client_2, update_modified=False)
				# self.client_id_2 = client_2
			
			if self.additional_members:
				for row in self.additional_members:
					if not row.client_id:
						client = create_client(row.first_name,row.last_name,row.gender,row.birth_date,row.qatar_id,row.mobile_no,row.email)
						frappe.db.set_value(row.doctype, row.name, "client_id", client, update_modified=False)

@frappe.whitelist()
def create_client(first_name,last_name,gender,birth_date,qatar_id,mobile_no,email):
	doc = frappe.get_doc({
		'doctype': 'Client',
		'first_name': first_name,
		'last_name' : last_name,
		'gender' : gender,
		'status' : 'Active',
		'membership_status' : 'Non-Member',
		'birth_date' : birth_date,
		'qatar_id' : qatar_id,
		'mobile_no' : mobile_no,
		'email': email,
		'default_currency' : 'QAR'
	})
	doc.save()
	return doc.name

# @frappe.whitelist()
# def create_membership(self):
# 	doc = frappe.get_doc({
# 		'doctype': 'Memberships',
# 		'primary_client_id': self.client_id,
# 		'membership_plan' : self.membership_plan,
# 		'client_id_1' : self.client_id,
# 		'client_id_2' : self.client_id_2,

@frappe.whitelist(allow_guest=True)
def mem_app(id):
	mem_app = frappe.get_doc("Memberships Application", id)
	return mem_app


	# 	plan= frappe.get_doc('Memberships Plan', self.membership_plan)
	# 	today = getdate()
	# 	expiry = today + timedelta(seconds=plan.duration)
	# 	if self.membership_type=="Single Membership":
	# 		if self.client_id_1:
	# 			doc = frappe.get_doc({
	# 				'doctype': 'Memberships',
	# 				'membership_application': self.name,
	# 				'client_id': self.client_id,
	# 				'start_date': today,
	# 				'end_date': expiry,
	# 				'client_id_1': self.client_id,
	# 				})
	# 			doc.insert()
	# 		else:
	# 			d = frappe.get_doc({
	# 				'doctype': 'Client',
	# 				'first_name': self.first_name_1,
	# 				'last_name': self.last_name_1,
	# 				'gender': self.gender_1,
	# 				'birth_date': self.birth_date_1,
	# 				'status': "Active",
	# 				'membership_status': "Member",
	# 				'reg_on_app': "No",
	# 				'qatar_id' : self.qatar_id_1,
	# 				'mobile_no': self.mobile_no_1,
	# 				'email': self.email_1,
	# 				'default_currency': 'QAR'
	# 				})
	# 			d.insert()
	# 			doc = frappe.get_doc({
	# 				'doctype': 'Memberships',
	# 				'membership_application': self.name,
	# 				'client_id': d.client_id,
	# 				'start_date': today,
	# 				'end_date': expiry,
	# 				'client_id_1': self.client_id,
	# 				})
	# 			doc.insert()