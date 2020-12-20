# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GroupClass(Document):

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