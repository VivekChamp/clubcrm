# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GroupClassAttendees(Document):
    def validate(self):
        doc = frappe.get_doc('Group Class',self.group_class)
        if doc.booking_status=="Full":
            frappe.throw('Group Class booking is full')
    
    def on_submit(self):
        gr_class=frappe.get_doc('Group Class',self.group_class)
        gr_class.remaining= int(gr_class.remaining)-1

        if gr_class.remaining==0:
            frappe.db.set_value('Group Class', self.group_class, {'booking_status': "Full",'remaining': gr_class.remaining})
        else:
            frappe.db.set_value('Group Class', self.group_class, 'remaining', gr_class.remaining)
        
    def on_cancel(self):
        gr_class=frappe.get_doc('Group Class',self.group_class)

        if gr_class.remaining==0:
            frappe.db.set_value('Group Class', self.group_class, {'booking_status': "Available",'remaining': int(gr_class.remaining)+1})
        else:
            frappe.db.set_value('Group Class', self.group_class, 'remaining', int(gr_class.remaining)+1)

