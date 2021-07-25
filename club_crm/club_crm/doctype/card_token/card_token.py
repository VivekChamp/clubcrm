# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class CardToken(Document):
	def validate(self):
		self.set_title()

	def set_title(self):
		card = self.last_4_digits_of_card
		card_digits = card[-4:]
		self.token_name = _('{0} ****{1}').format(self.card_type, card_digits)