# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, date
from frappe.utils import getdate, get_time, flt

class GroupClassAttendees(Document):
    def before_insert(self):
        check = frappe.get_all('Group Class Attendees', filters={'group_class':self.group_class, 'client_id':self.client_id, 'attendee_status': ['not in',{'Cancelled'}]})
        if check:
            frappe.throw('This member has already enrolled for this Group Class')
        doc = frappe.get_doc('Group Class', self.group_class)
        if doc. waitlist != 0 and doc.in_waitlist == doc.waitlist:
            frappe.throw('No more slots available for this group class.')
            
    def validate(self):
        self.set_attendee_status()

    def after_insert(self):
        if self.attendee_status == "Open" or self.attendee_status == "Scheduled":
            group_class = frappe.get_doc('Group Class', self.group_class)
            group_class.booked += 1
            group_class.save()
            if group_class.remaining == 0:
                frappe.db.set_value('Group Class', self.group_class, 'booking_status', 'Full')
                frappe.db.commit()
        
        if self.attendee_status == "Waiting List":
            group_class = frappe.get_doc('Group Class', self.group_class)
            group_class.in_waitlist += 1
            group_class.save()

    def set_attendee_status(self):
        today = getdate()
        group_class = frappe.get_doc('Group Class', self.group_class)
        if not self.attendee_status == "Complete" or not self.attendee_status == "Cancelled" or not self.attendee_status == "Checked-in" or self.attendee_status != "No Show" or self.attendee_status == "":
            if group_class.remaining > 0:
                if self.class_date == today:
                    self.attendee_status = "Open"
                else:
                    self.attendee_status = "Scheduled"
            elif group_class.remaining == 0 and group_class.in_waitlist < group_class.waitlist:
                self.attendee_status = "Waiting List"
            elif group_class.remaining == 0:
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
        if not self.attendee_status == "Complete":
            if self.attendee_status == today:
                self.attendee_status = "Open"
            elif self.attendee_status > today:
                self.attendee_status = "Scheduled"


@frappe.whitelist()
def cancel_attendee(group_class_attendee_id):
    doc = frappe.get_doc('Group Class Attendees', group_class_attendee_id )
    frappe.db.set_value('Group Class Attendees', group_class_attendee_id, {
        'attendee_status': "Cancelled",
        'docstatus': 2
        })
    frappe.db.commit()
    
    group_class = frappe.get_doc('Group Class', doc.group_class)

    if doc.attendee_status == "Open" or doc.attendee_status == "Scheduled":
        group_class.booked -= 1
        group_class.save()
        
    elif doc.attendee_status == "Waiting List":
        group_class.in_waitlist -= 1
        group_class.save()
    
    if group_class.booking_status == "Full" and not 0 < group_class.in_waitlist <= group_class.waitlist and group_class.remaining > 0:
        frappe.db.set_value('Group Class', group_class.name, 'booking_status', 'Available')
        frappe.db.commit()

    frappe.msgprint(msg="Member has been unenrolled from the group class", title='Success')

@frappe.whitelist()
def confirm_attendee(group_class_attendee_id):
    doc = frappe.get_doc('Group Class Attendees', group_class_attendee_id )
    group_class = frappe.get_doc('Group Class', doc.group_class)
    if group_class.remaining > 0:
        group_class.booked += 1
        group_class.in_waitlist -= 1
        group_class.save()
        doc.attendee_status = "Scheduled"
        doc.save()
    else:
        frappe.throw('No free slots available for this group class yet.')