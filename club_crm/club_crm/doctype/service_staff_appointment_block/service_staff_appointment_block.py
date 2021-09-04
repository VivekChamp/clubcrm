# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime, timedelta, date, time
from frappe.utils import getdate, get_time, flt, now_datetime

class ServiceStaffAppointmentBlock(Document):
	def validate(self):
		self.set_datetime()
		self.check_overlap()
		self.set_title()

	def set_datetime(self):
		from_time = convert24(self.from_time)
		self.from_time_dt = datetime.strptime(from_time, "%H:%M:%S")
		to_time = convert24(self.to_time)
		self.to_time_dt = datetime.strptime(to_time, "%H:%M:%S")

		self.from_datetime = datetime.combine(getdate(self.date), get_time(self.from_time_dt))
		self.to_datetime = datetime.combine(getdate(self.date), get_time(self.to_time_dt))

	def check_overlap(self):
		pass

	def set_title(self):
		date_dt = datetime.strptime(self.date, "%Y-%m-%d")
		date = datetime.strftime(date_dt, "%d-%m-%Y")
		self.title = _('{0} for {1}').format(self.staff_name, date)

@frappe.whitelist()
def convert24(str1):
	if str1[-3:] == " AM" and str1[:2] == "12":
		return "00" + str1[2:-3]
	elif str1[-3:] == " AM":
		return str1[:-3]
	elif str1[-3:] == " PM" and str1[:2] == "12":
		return str1[:-3]
	else:
		return str(int(str1[:2]) + 12) + str1[2:8]