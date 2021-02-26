# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from datetime import datetime, timedelta
from frappe.utils import getdate, get_time, flt
from frappe.model.document import Document

class Memberships(Document):
	def validate(self):
		self.calculate_expiry()
		self.set_member_number()
		
	def calculate_expiry(self):
		if not self.end_date:
			start_date= datetime.strptime(self.start_date, "%Y-%m-%d")
			expiry_date= start_date + timedelta(days=int(self.duration))
			self.end_date= expiry_date.strftime("%Y-%m-%d")

	def set_member_number(self):
		if self.client_id_1:
			frappe.db.set_value('Client', self.client_id_1, 'member_id', self.member_no_1)
			frappe.db.set_value('Client', self.client_id_1, 'card_no', self.card_no_1)
			frappe.db.set_value('Client', self.client_id_1, 'membership_no', self.membership_id)
			frappe.db.commit()


	def on_submit(self):
		if self.membership_type == 'Single Membership':
			customer = frappe.db.get_value('Customer', {"client_id":self.client_id_1 },'name')
			if customer:
				frappe.db.set_value('Customer', customer, 'member_id', self.member_no_1)
		if self.membership_type == 'Couple Membership' or 'Family Membership':
			customer1 = frappe.db.get_value('Customer', {"client_id":self.client_id_1},'name')
			customer2 = frappe.db.get_value('Customer', {"client_id":self.client_2},'name')
			if customer1 and customer2:
				frappe.db.set_value('Customer', customer1, 'member_id', self.member_no_1)
				frappe.db.set_value('Customer', customer2, 'member_id', self.member_no_2)

		if self.membership_type == 'Family Membership':
			additional_member_details = frappe.db.get_all('Additional Members Item', {'parent': self.name}, ['client_id', 'member_id'])
			for row in additional_member_details:
				customer = frappe.db.get_value('Customer', {"client_id":self.client_id},'name')
				frappe.db.set_value('Customer', customer, 'member_id', self.member_id)
		
		
