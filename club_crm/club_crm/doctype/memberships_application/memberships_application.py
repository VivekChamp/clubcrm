# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MembershipsApplication(Document):
	def validate(self):
			self.calculate_total()

	def before_insert(self):
			self.check_existing_application()
			self.check_primary_client_id()
		
	def check_primary_client_id(self):
			if self.submitted_by_staff==1:
					client1_all= frappe.get_all('Client', filters={'mobile_no':self.mobile_no_1})
					if client1_all:
							client_1 = client1_all[0]
							self.client_id_1=client_1.name
			else:
				details=frappe.get_doc('Client', self.client_id)
				self.first_name_1=details.first_name
				self.last_name_1=details.last_name
				self.birth_date_1= details.birth_date
				self.gender_1= details.gender
				self.mobile_no_1= details.mobile_no
				self.email_1= details.email
				self.client_id_1= self.client_id

	def check_other_client_id(self):
			client2_all= frappe.get_all('Client', filters={'mobile_no':self.mobile_no_2})
			if client2_all:
					client_2 = client2_all[0]
					self.client_id_2=client_2.name

	def check_existing_application(self):
			mem_app= frappe.get_all('Memberships Application', filters={'qatar_id_1':self.qatar_id_1,'application_status':"Pending"})
			if mem_app:
					frappe.throw('A pending Membership Application already exists. Kindly wait until it is reviewed.')

	def calculate_total(self):
			self.net_total = self.membership_fee + self.joining_fee
			if not self.discount_amount:
				self.grand_total = self.net_total
			elif self.discount_amount>self.net_total:
				frappe.throw('The discount amount is greater than Total Membership amount')
			else:
				self.grand_total = self.net_total - self.discount_amount

	def on_submit(self):
			mem_apply= frappe.get_doc('Client', self.client_id)
			mem_apply.apply_membership==1
			mem_apply.save()
