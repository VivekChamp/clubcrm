# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from frappe import _
from frappe.model.document import Document

class PaymentLog(Document):
	def validate(self):
		self.set_title()
	
	# def on_submit(self):
	# 	self.make_paid()
	
	def set_title(self):
		self.title = _('{0} {1} for {2}').format(self.req_bill_to_forename, self.req_bill_to_surname, self.req_reference_number)

	def make_paid(self):
		# if self.signature_verified==1:
		# 	if self.decision=="ACCEPT" and self.req_amount==self.auth_amount:
		doc = frappe.get_doc('Memberships Application', self.req_reference_number)
		if doc:
			doc.payment_status = 'Paid'
			doc.save()
				# frappe.db.set_value("Memberships Application",str(self.req_reference_number),"payment_status","Paid")
				# doc = frappe.get_doc("Memberships Application",str(self.req_reference_number))
				# doc.save()

@frappe.whitelist()
def make_paid(doc, method=None):
	mem_app = frappe.get_doc('Memberships Application', doc.req_reference_number)
	if mem_app:
		mem_app.payment_status = "Paid"
		mem_app.save()
