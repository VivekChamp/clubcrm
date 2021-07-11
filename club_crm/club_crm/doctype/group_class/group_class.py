# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, get_time, flt
from datetime import datetime, timedelta, date

class GroupClass(Document):
    def validate(self):
        self.set_datetime()
        self.set_title()
        self.set_remaining()
        self.set_status()

    def set_datetime(self):
        class_from_time = convert24(self.class_from_time)
        self.from_time = "%s %s" % (self.class_date, class_from_time or "00:00:00")

        class_to_time = convert24(self.class_to_time)
        self.to_time = "%s %s" % (self.class_date, class_to_time or "00:00:00")

    def set_title(self):
        self.title = _('{0} with {1}').format(self.group_class_name,self.trainer_name)

    def set_remaining(self):
        self.remaining = self.capacity - self.booked
        if self.remaining == 0:
            self.booking_status = 'Full'
            # frappe.db.set_value('Group Class', self.name, 'booking_status', 'Full')
            # frappe.db.commit()
        elif self.remaining > 0:
            self.booking_status = 'Available'
            # frappe.db.set_value('Group Class', self.name, 'booking_status', 'Available')
            # frappe.db.commit()

    # def set_status(self):
    #     today = getdate()
	# 	# If appointment is created for today set status as Open else Scheduled
    #     if not self.class_status == "Complete" or not self.class_status == "Cancelled" or self.class_status == "":
    #         if self.class_date == today:
    #             attendees = frappe.get_all('Group Class Attendees', filters={'group_class': self.name})
    #             for attendee in attendees:
    #                 frappe.db.set_value("Group Class Attendees", attendee.name, "class_status", "Open")
    #                 frappe.db.commit()
    #             self.class_status = "Open"
    #         elif self.class_date > today:
    #             attendees = frappe.get_all('Group Class Attendees', filters={'group_class': self.name})
    #             for attendee in attendees:
    #                 frappe.db.set_value("Group Class Attendees", attendee.name, "class_status", "Scheduled")
    #                 frappe.db.commit()
    #             self.class_status = "Scheduled"

    # def on_update_after_submit(self):
    #     if self.class_status =='Completed':
    #         doc= frappe.get_all('Group Class Attendees', filters={'group_class':self.name, 'docstatus':1}, fields=["*"])
    #         for name in doc:
    #             if name.checked_in=='Yes':
    #                 frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'Completed')
    #             else:
    #                 frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'No Show')
    #         frappe.db.commit()

    #     elif self.class_status == "Cancelled":
    #         doc = frappe.get_all('Group Class Attendees', filters={'group_class':self.name, 'docstatus':1}, fields=["*"])
    #         for name in doc:
    #             frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'Cancelled')
    #         frappe.db.commit()

    #     elif self.class_status == "Open":
    #         doc = frappe.get_all('Group Class Attendees', filters={'group_class':self.name, 'docstatus':1}, fields=["*"])
    #         for name in doc:
    #             frappe.db.set_value('Group Class Attendees', name.name, 'class_status', 'Open')
    #         frappe.db.commit()

    def set_status(self):
        today = getdate()
        class_date= datetime.strptime(str(self.from_time), '%Y-%m-%d %H:%M:%S')
        date = class_date.date()

		# If appointment is created for today set status as Open else Scheduled
        if not self.class_status == "Complete":
            if date == today:
                self.class_status = "Open"
                attendees = frappe.get_all('Group Class Attendees', filters={'group_class': self.name, 'attendee_status': ['not in', {'Waiting List', 'Cancelled'}]})
                if attendees:
                    for attendee in attendees:
                        frappe.db.set_value("Group Class Attendees", attendee.name, "attendee_status", "Open")
            elif date > today:
                self.class_status = "Scheduled"
                attendees = frappe.get_all('Group Class Attendees', filters={'group_class': self.name, 'attendee_status': ['not in', {'Waiting List', 'Cancelled'}]})
                if attendees:
                    for attendee in attendees:
                        frappe.db.set_value("Group Class Attendees", attendee.name, "attendee_status", "Scheduled")

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

@frappe.whitelist()
def cancel_class(group_class_id):
    frappe.db.set_value('Group Class', group_class_id, {
        'class_status': "Cancelled",
        'docstatus': 2
    })
    frappe.db.commit()

    gc_attendees =  frappe.get_all('Group Class Attendees', filters={'group_class': group_class_id})
    if gc_attendees:
        for attendee in gc_attendees:
            frappe.db.set_value('Group Class Attendees', attendee.name, {
                'attendee_status': "Cancelled",
                'docstatus': 2
            })
            frappe.db.commit()

    frappe.msgprint(msg="Group Class has been cancelled", title='Success')

@frappe.whitelist()
def complete_class(group_class_id):
    # group_class = frappe.get_doc('Group Class', group_class_id)
    frappe.db.set_value('Group Class', group_class_id, {
        'class_status': "Completed",
        'docstatus': 1
    })
    frappe.db.commit()

    gc_attendees =  frappe.get_all('Group Class Attendees', filters={'group_class': group_class_id, 'attendee_status': 'Checked-in'})
    if gc_attendees:
        for attendee in gc_attendees:
            frappe.db.set_value('Group Class Attendees', attendee.name, {
                'attendee_status': "Complete",
                'docstatus': 1
            })
            frappe.db.commit()

    frappe.msgprint(msg="Group Class completed", title='Success')

@frappe.whitelist()
def update_gc_status():
    today = getdate()
    group_classes = frappe.get_all('Group Class', filters={'class_status': ('not in', ['Completed', 'Cancelled'])}, fields=['name','class_status'])
    if group_classes:
        for gc in group_classes:
            class_date= datetime.strptime(str(gc.from_time), '%Y-%m-%d %H:%M:%S')
            date = class_date.date()

		    # If appointment is created for today set status as Open else Scheduled
            if date == today:
                gc.class_status = "Open"
                gc.save()
                attendees = frappe.get_all('Group Class Attendees', filters={'group_class': gc.name, 'attendee_status': ['not in', {'Waiting List', 'Cancelled'}]})
                if attendees:
                    for attendee in attendees:
                        frappe.db.set_value("Group Class Attendees", attendee.name, "attendee_status", "Open")
                        frappe.db.commit()
            elif date > today:
                gc.class_status = "Scheduled"
                gc.save()
                attendees = frappe.get_all('Group Class Attendees', filters={'group_class': gc.name, 'attendee_status': ['not in', {'Waiting List', 'Cancelled'}]})
                if attendees:
                    for attendee in attendees:
                        frappe.db.set_value("Group Class Attendees", attendee.name, "attendee_status", "Scheduled")
                        frappe.db.commit()