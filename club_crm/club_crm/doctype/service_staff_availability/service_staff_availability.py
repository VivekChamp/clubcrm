# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import calendar
import datetime
from dateutil import relativedelta
from datetime import timedelta
from frappe.model.document import Document
from frappe.utils import getdate, formatdate, today
from frappe import throw, msgprint, _

class ServiceStaffAvailability(Document):
	def validate(self):
		self.set_title()
		for i, item in enumerate(sorted(self.week_1, key=lambda item: str(item.date))):
			item.idx = i
		for i, item in enumerate(sorted(self.week_2, key=lambda item: str(item.date))):
			item.idx = i
		for i, item in enumerate(sorted(self.week_3, key=lambda item: str(item.date))):
			item.idx = i
		for i, item in enumerate(sorted(self.week_4, key=lambda item: str(item.date))):
			item.idx = i
		for i, item in enumerate(sorted(self.week_5, key=lambda item: str(item.date))):
			item.idx = i
		for i, item in enumerate(sorted(self.week_6, key=lambda item: str(item.date))):
			item.idx = i
		
	def set_title(self):
		self.title = _('{0} for {1} {2}').format(self.staff_name, self.month, self.year)

	def add_schedule(self):
		self.validate_values()
		if not self.end_date:
			date_list = self.add_schedule_list_single(self.start_date)
		elif self.end_date and not self.day:
			date_list = self.add_schedule_list_daily(self.start_date,self.end_date)
		else:
			date_list = self.add_schedule_list(self.start_date, self.end_date)
		
		for date in date_list:
			week = date.isocalendar()[1] - date.replace(day=1).isocalendar()[1] + 1
			if week == 1:
				add_day = self.append('week_1', {})
				add_day.date = date
				weekdate = get_weekday(date)
				add_day.day = weekdate
				add_day.from_time = self.from_time
				add_day.to_time = self.to_time
			if week == 2:
				add_day = self.append('week_2', {})
				add_day.date = date
				weekdate = get_weekday(date)
				add_day.day = weekdate
				add_day.from_time = self.from_time
				add_day.to_time = self.to_time
			if week == 3:
				add_day = self.append('week_3', {})
				add_day.date = date
				weekdate = get_weekday(date)
				add_day.day = weekdate
				add_day.from_time = self.from_time
				add_day.to_time = self.to_time
			if week == 4:
				add_day = self.append('week_4', {})
				add_day.date = date
				weekdate = get_weekday(date)
				add_day.day = weekdate
				add_day.from_time = self.from_time
				add_day.to_time = self.to_time
			if week == 5:
				add_day = self.append('week_5', {})
				add_day.date = date
				weekdate = get_weekday(date)
				add_day.day = weekdate
				add_day.from_time = self.from_time
				add_day.to_time = self.to_time
			if week == 6:
				add_day = self.append('week_6', {})
				add_day.date = date
				weekdate = get_weekday(date)
				add_day.day = weekdate
				add_day.from_time = self.from_time
				add_day.to_time = self.to_time

	def validate_values(self):
		if not self.start_date:
			frappe.throw(_("Please select a date for the schedule"))
		if not self.from_time:
			frappe.throw(_("Please select the start time"))
		if not self.to_time:
			frappe.throw(_("Please select the end time"))

	def add_schedule_list(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		date_list = []
		weekday = getattr(calendar, (self.day).upper())
		reference_date = start_date + relativedelta.relativedelta(weekday=weekday)

		while reference_date <= end_date:
			date_list.append(reference_date)
			reference_date += timedelta(days=7)

		return date_list
	
	def add_schedule_daily(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		date_list = []
		while start_date <= end_date:
			date_list.append(start_date)
			start_date += timedelta(days=1)

		return date_list

	def add_schedule_list_single(self, start_date):
		start_date = getdate(start_date)

		date_list = []
		date_list.append(start_date)

		return date_list

@frappe.whitelist()
def get_weekday(date):
	day_name = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
	weekday = day_name[date.weekday()]
	return weekday