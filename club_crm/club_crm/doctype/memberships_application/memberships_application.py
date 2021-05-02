# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta
from club_crm.club_crm.doctype.client_sessions.client_sessions import create_session
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.model.document import Document

class MembershipsApplication(Document):
	def before_insert(self):
		self.check_existing_application()

	def after_insert(self):
		if self.online_application==0:
			frappe.db.set_value('Memberships Application', self.name, 'workflow_status', 'Pending')
		# self.send_notification()

	def validate(self):
		self.check_clients()
		self.check_birthdate()
		self.set_pricing()
		self.set_discounts_and_grand_total()
		self.set_payment_details()
		self.set_title()
		# self.validate_submit()
	
	def before_submit(self):
		self.check_payment()

	def on_submit(self):
		self.create_clients()
		self.update_client_details()

	def on_cancel(self):
		frappe.db.set_value('Memberships Application', self.name, {
			'workflow_status': 'Cancelled',
			'application_status': 'Cancelled'
		})

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
	
		if self.online_application==0:
			if self.client_id:
				frappe.db.set_value('Client', self.client_id, 'apply_membership', 1)
				frappe.db.set_value('Client', self.client_id, 'mem_application', self.name)
				frappe.db.commit()

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
		self.joining_fee = 0.0
		self.membership_fee_adult = 0.0
		self.membership_fee_child = 0.0
		self.total_membership_fee = 0.0
		self.net_total = 0.0
		
		mem_plan = frappe.get_doc('Memberships Plan', self.membership_plan)
		if self.application_type == "New":
			self.joining_fee = mem_plan.joining_fee_adult * float(self.no_of_adults)
		self.membership_fee_adult = mem_plan.membership_fee_adult * float(self.no_of_adults)
		
		if self.membership_type == "Family Membership":
			if self.no_of_children == 1 and self.no_of_adults == 2:
				self.membership_fee_child = mem_plan.membership_fee_child * 2
			else:
				self.membership_fee_child = mem_plan.membership_fee_child * float(self.no_of_children)

		self.total_membership_fee = self.membership_fee_adult + self.membership_fee_child
		self.net_total = self.joining_fee + self.total_membership_fee

	def set_discounts_and_grand_total(self):
		self.discount_amount = 0.0
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
		self.balance_amount = 0.0
		self.total_to_be_paid = self.grand_total
		if self.membership_payment:
			for row in self.membership_payment:
				self.paid_amount += float(row.paid_amount)
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

	def update_client_details(self):
		if self.client_id:
			doc = frappe.get_doc('Client', self.client_id)
			doc.occupation = self.occupation_1
			doc.company = self.company_1
			doc.birth_date = self.birth_date_1
			doc.qatar_id = self.qatar_id_1
			doc.nationality = self.nationality_1
			if not doc.email:
				doc.email = self.email_1
			doc.save()
		
		if self.client_id_2:
			doc = frappe.get_doc('Client', self.client_id_2)
			doc.occupation = self.occupation_2
			doc.company = self.company_2
			doc.birth_date = self.birth_date_2
			doc.qatar_id = self.qatar_id_2
			doc.nationality = self.nationality_2
			if not doc.email:
				doc.email = self.email_2
			doc.save()
		
		if self.additional_members:
			for row in self.additional_members:
				if row.client_id and row.category=="Adult":
					doc = frappe.get_doc('Client', row.client_id)
					doc.birth_date = row.birth_date
					doc.qatar_id = row.qatar_id
					doc.nationality = row.nationality
					if not doc.email:
						doc.email = row.email
					doc.save()

	# def send_notification(self):
	# 	settings = frappe.get_doc('Memberships Settings')
	# 	if settings.enabled==1 and self.online_application==1:
	# 		msg = "New membership application has been received from "+self.first_name_1+" "+self.last_name_1+"."
	# 		receiver_list='"'+settings.mobile_no+'"'
	# 		send_sms(receiver_list,msg)

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

@frappe.whitelist()
def create_membership(mem_application_id):
	mem_app = frappe.get_doc('Memberships Application', mem_application_id)
	mem_plan = frappe.get_doc('Memberships Plan', mem_app.membership_plan)

	doc = frappe.new_doc("Memberships")
	doc.primary_client_id = mem_app.client_id
	doc.membership_plan = mem_app.membership_plan
	doc.client_id_1 = mem_app.client_id
	doc.assigned_to_1 = mem_app.assigned_to
	if mem_app.membership_type == "Couple Membership":
		doc.client_id_2 = mem_app.client_id_2
		doc.assigned_to_2 = mem_app.assigned_to
	if mem_app.membership_type == "Family Membership":
		doc.client_id_2 = mem_app.client_id_2
		doc.assigned_to_2 = mem_app.assigned_to
		for row in mem_app.additional_members:
		# 	# child = doc.append("additional_members_item", {})
		# 	# child.client_id = row.client_id
		# 	# child.assigned_to = mem_app.assigned_to
			doc.append('additional_members_item', {
				'client_id': row.client_id,
				'assigned_to': mem_app.assigned_to
			})
	doc.membership_application = mem_application_id
	doc.total_amount = float(mem_app.grand_total)
	doc.save()
	frappe.db.set_value("Memberships Application", mem_application_id, "membership_document", doc.name, update_modified=False)
	
	# club_package = frappe.get_doc('Club Packages', mem_plan.benefits_item)
	# if club_package.package_table:
	# 	for item in club_package.package_table:
	# 		create_session(mem_app.client_id,mem_plan.benefits_item,item.service_type,item.service_name,item.no_of_sessions,item.validity)
	# 		if mem_app.membership_type == "Couple Membership":
	# 			create_session(mem_app.client_id_2,mem_plan.benefits_item,item.service_type,item.service_name,item.no_of_sessions,item.validity)
	# 		if mem_app.membership_type == "Family Membership":
	# 			create_session(mem_app.client_id_2,mem_plan.benefits_item,item.service_type,item.service_name,item.no_of_sessions,item.validity)
	# 			for row in mem_app.additional_members:
	# 				if row.category == "Adult":
	# 					create_session(row.client_id,mem_plan.benefits_item,item.service_type,item.service_name,item.no_of_sessions,item.validity)
	frappe.msgprint(msg = "Membership created successfully. Please verify the membership details and set it Active to make the member(s) active ", title="Success")

@frappe.whitelist()
def update_payment(docname, amount):
	doc = frappe.get_doc("Memberships Application", docname)
	doc.append('membership_payment', {
		"mode_of_payment": "Online Payment",
		"paid_amount": amount
	})
	doc.payment_status = "Paid"
	doc.save()

# @frappe.whitelist()
# def renew_membership_single(source_name, target_doc=None):
# 	def set_missing_values(source, target):
# 		target.application_type = 'Renew'
# 		target.existing_client_1 = 1

# 	doc = get_mapped_doc('Memberships', source_name, {
# 			'Memberships': {
# 				'doctype': 'Memberships Application',
# 				'field_map': {
# 					'membership_category': 'membership_category',
# 					'membership_plan': 'membership_plan',
# 					'assigned_to': 'assigned_to_1',
# 					'client_id': 'client_id_1',
# 					'occupation_1': 'client_id_1',
# 					'company_1': 'client_id_1'
# 				}
# 			}
# 		}, target_doc)
# 	return doc