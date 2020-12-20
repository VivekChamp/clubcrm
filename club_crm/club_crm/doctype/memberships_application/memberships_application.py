# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MembershipsApplication(Document):
	def before_insert(self):
			self.check_existing_application()
			self.check_primary_client_id()

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
