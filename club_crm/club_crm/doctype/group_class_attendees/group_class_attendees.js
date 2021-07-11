// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Group Class Attendees", "onload", function(frm) {
    //Show only active classes in group class field 
    frm.set_query("group_class", function() {
        return {
            "filters": [
                ["Group Class", "class_status", "in", ["Open", "Scheduled"]]
            ]
        }
    });
});

frappe.ui.form.on('Group Class Attendees', {
    refresh: function(frm) {
        if (!frm.is_new() && (frm.doc.attendee_status == "Open")) {
            frappe.call({
                method: 'club_crm.club_crm.doctype.client.client.check_status',
                args: { client_id: frm.doc.client_id },
                callback: function(r) {
                    if (r.message == "Checked-in") {
                        frm.add_custom_button(__('Check-In'), function() {
                            frappe.call({
                                method: 'club_crm.club_crm.doctype.check_in.check_in.gc_checkin',
                                args: { client_id: frm.doc.client_id, doc_id: frm.doc.name },
                                callback: function(r) {
                                    cur_frm.reload_doc();
                                }
                            });
                        });

                        frm.page.add_menu_item(__("Check-in"), function() {
                            frappe.call({
                                method: 'club_crm.club_crm.doctype.check_in.check_in.gc_checkin',
                                args: { client_id: frm.doc.client_id, doc_id: frm.doc.name },
                                callback: function(r) {
                                    cur_frm.reload_doc();
                                }
                            });
                        });
                    }
                }
            });
        }

        // Cancel a Group Class
        if (!frm.is_new() && (frm.doc.attendee_status == "Scheduled" || frm.doc.attendee_status == "Open" || frm.doc.attendee_status == "Waiting List")) {
            frm.add_custom_button(__('Cancel'), function() {
                frappe.confirm('Please confirm to cancel this group class attendee',
                    () => {
                        // action to perform if Yes is selected
                        frappe.call({
                            method: 'club_crm.club_crm.doctype.group_class_attendees.group_class_attendees.cancel_attendee',
                            args: { group_class_attendee_id: frm.doc.name },
                            callback: function(r) {
                                cur_frm.reload_doc();
                            }
                        });
                    }, () => {
                        // action to perform if No is selected
                    })
            }, __("Set"));

            frm.page.add_menu_item(__("Cancel"), function() {
                frappe.confirm('Please confirm to cancel this group class attendee',
                    () => {
                        // action to perform if Yes is selected
                        frappe.call({
                            method: 'club_crm.club_crm.doctype.group_class_attendees.group_class_attendees.cancel_attendee',
                            args: { group_class_attendee_id: frm.doc.name },
                            callback: function(r) {
                                cur_frm.reload_doc();
                            }
                        });
                    }, () => {
                        // action to perform if No is selected
                    })
            });
        }

        if (!frm.is_new() && frm.doc.attendee_status == "Waiting List") {
            frm.add_custom_button(__('Scheduled'), function() {
                frappe.confirm('Please confirm to book this member for the group class',
                    () => {
                        // action to perform if Yes is selected
                        frappe.call({
                            method: 'club_crm.club_crm.doctype.group_class_attendees.group_class_attendees.confirm_attendee',
                            args: { group_class_attendee_id: frm.doc.name },
                            callback: function(r) {
                                cur_frm.reload_doc();
                            }
                        });
                    }, () => {
                        // action to perform if No is selected
                    })

            }, __("Set"));
        }
    }
});