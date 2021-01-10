# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta
from frappe.model.document import Document

class MembershipsApplication(Document):
	def before_insert(self):
			self.check_existing_application()
			self.check_primary_client_id()
			if self.first_name_2:
				self.check_second_client_id()

	def check_primary_client_id(self):
			if self.submitted_by_staff==1:
					client1_all= frappe.get_all('Client', filters={'mobile_no':self.mobile_no_1})
					if client1_all:
							client_1 = client1_all[0]
							self.client_id_1=client_1.client_id
			else:
				details=frappe.get_doc('Client', self.client_id)
				self.first_name_1=details.first_name
				self.last_name_1=details.last_name
				self.birth_date_1= details.birth_date
				self.gender_1= details.gender
				self.mobile_no_1= details.mobile_no
				self.email_1= details.email
				self.client_id_1= self.client_id

	def check_existing_application(self):
			mem_app= frappe.get_all('Memberships Application', filters={'qatar_id_1':self.qatar_id_1,'application_status':"Pending"})
			if mem_app:
					frappe.throw('A pending Membership Application already exists. Kindly wait until it is reviewed.')

	def check_second_client_id(self):
		client= frappe.get_all('Client', filters={'mobile_no':self.mobile_no_2})
		if client:
			client_2= client[0]
			self.client_id_2= client_2.client_id

	def on_update_after_submit(self):
		if self.payment_status=="Paid":
			# self.create_invoice()
			self.create_membership()

	def create_membership(self):
		plan= frappe.get_doc('Memberships Plan', self.membership_plan)
		today = getdate()
		expiry = today + timedelta(seconds=plan.duration)
		if self.membership_type=="Single Membership":
			if self.client_id_1:
				doc = frappe.get_doc({
					'doctype': 'Memberships',
					'membership_application': self.name,
					'client_id': self.client_id,
					'start_date': today,
					'end_date': expiry,
					'client_id_1': self.client_id,
					})
				doc.insert()
			else:
				d = frappe.get_doc({
					'doctype': 'Client',
					'first_name': self.first_name_1,
					'last_name': self.last_name_1,
					'gender': self.gender_1,
					'birth_date': self.birth_date_1,
					'status': "Active",
					'membership_status': "Member",
					'reg_on_app': "No",
					'qatar_id' : self.qatar_id_1,
					'mobile_no': self.mobile_no_1,
					'email': self.email_1,
					'default_currency': 'QAR'
					})
				d.insert()
				doc = frappe.get_doc({
					'doctype': 'Memberships',
					'membership_application': self.name,
					'client_id': d.client_id,
					'start_date': today,
					'end_date': expiry,
					'client_id_1': self.client_id,
					})
				doc.insert()