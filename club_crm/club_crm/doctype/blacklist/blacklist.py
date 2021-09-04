# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Blacklist(Document):
	def validate(self):
		self.set_title

	def set_title(self):
		self.title = _('{0} for {1}').format(self.client_name, self.servicse_staff)