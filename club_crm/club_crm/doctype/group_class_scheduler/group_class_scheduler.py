# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, getdate, formatdate, today
from frappe import throw, msgprint, _


class GroupClassScheduler(Document):
	def add_class_dates(self):
		self.validate_values()
		date_list = self.add_class_dates_list(self.start_date, self.end_date)
		last_idx = max([cint(d.idx) for d in self.get("details")] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append('details', {})
			ch.date = d
			ch.idx = last_idx + i + 1

	def validate_values(self):
		if not self.class_day:
			frappe.throw(_("Please select Group Class Day"))

	def add_class_dates_list(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		from dateutil import relativedelta
		from datetime import timedelta
		import calendar

		date_list = []
		weekday = getattr(calendar, (self.class_day).upper())
		reference_date = start_date + relativedelta.relativedelta(weekday=weekday)

		while reference_date <= end_date:
			date_list.append(reference_date)
			reference_date += timedelta(days=7)

		return date_list

	def clear_table(self):
		self.set('details', [])