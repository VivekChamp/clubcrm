# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date
from frappe.utils import getdate, get_time, flt

class GroupClassAttendees(Document):
    def validate(self):
        self.set_status()
        doc = frappe.get_doc('Group Class', self.group_class)
        if doc.booking_status=="Full":
            frappe.throw('Group Class booking is full')
    
    def on_submit(self):
        gr_class=frappe.get_doc('Group Class',self.group_class)
        gr_class.remaining= int(gr_class.remaining)-1

        if gr_class.remaining==0:
            frappe.db.set_value('Group Class', self.group_class, {'booking_status': "Full",'remaining': gr_class.remaining})
            frappe.db.commit()
        else:
            frappe.db.set_value('Group Class', self.group_class, 'remaining', gr_class.remaining)
            frappe.db.commit()
        
    def on_cancel(self):
        frappe.db.set_value('Group Class Attendees', self.name, 'class_status', 'Cancelled')
        gr_class=frappe.get_doc('Group Class',self.group_class)
        if gr_class.remaining==0:
            frappe.db.set_value('Group Class', self.group_class, {'booking_status': "Available",'remaining': int(gr_class.remaining)+1})
            frappe.db.commit()
        else:
            frappe.db.set_value('Group Class', self.group_class, 'remaining', int(gr_class.remaining)+1)
            frappe.db.commit()
        
    def set_status(self):
        today = getdate()
        # If appointment is created for today set status as Open else Scheduled
        if not self.class_status == "Complete":
            if self.class_date == today:
                self.class_status = "Open"
            elif self.class_date > today:
                self.class_status = "Scheduled"