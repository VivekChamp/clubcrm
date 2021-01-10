# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date

class GroupClass(Document):
    def validate(self):
        self.set_status()

    def before_save(self):
        self.remaining = self.capacity

    def on_update_after_submit(self):
        if self.class_status =='Completed':
            doc= frappe.get_all('Group Class Attendees', filters={'group_class':self.name, 'docstatus':1}, fields=["*"])
            for name in doc:
                if name.checked_in=='Yes':
                    frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'Completed')
                else:
                    frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'No Show')
            frappe.db.commit()

        elif self.class_status == "Cancelled":
            doc = frappe.get_all('Group Class Attendees', filters={'group_class':self.name, 'docstatus':1}, fields=["*"])
            for name in doc:
                frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'Cancelled')
            frappe.db.commit()

        elif self.class_status == "Open":
            doc = frappe.get_all('Group Class Attendees', filters={'group_class':self.name, 'docstatus':1}, fields=["*"])
            for name in doc:
                frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'Open')
            frappe.db.commit()

    def set_status(self):
        today = getdate()
        class_date= datetime.strptime(str(self.from_time), '%Y-%m-%d %H:%M:%S')
        date= class_date.date()

		# If appointment is created for today set status as Open else Scheduled
        if not self.class_status == "Complete":
            if date == today:
                self.class_status = "Open"
            elif date > today:
                self.class_status = "Scheduled"