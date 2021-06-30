// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Group Class", "onload", function(frm) {
    frm.set_query("group_class_name", function() {
        return {
            "filters": [
                ["Group Class Services", "enabled", "=", 1]
            ]
        }
    });
    frm.set_query("location", function() {
        return {
            "filters": [
                ["Club Room", "club_room_type", "=", "Fitness"],
                ["Club Room", "is_group", "=", "0"]
            ]
        }
    });
    frm.set_query("trainer_name", function() {
        return {
            "filters": [
                ["Service Staff", "fitness_check", "=", 1]
            ]
        }
    });
});

frappe.ui.form.on('Group Class', {
    refresh: function(frm) {
        if (frm.doc.class_status == "Scheduled" || frm.doc.class_status == "Open") {
            frm.add_custom_button(__('Cancel'), function() {
                frappe.confirm('Please confirm to cancel this group class',
                    () => {
                        // action to perform if Yes is selected
                        frappe.call({
                            method: 'club_crm.club_crm.doctype.group_class.group_class.cancel_class',
                            args: { group_class_id: frm.doc.name },
                            callback: function(r) {
                                cur_frm.reload_doc();
                            }
                        });
                    }, () => {
                        // action to perform if No is selected
                    })
            }, __("Set"));
        }
        if (frm.doc.class_status == "Open") {
            frm.add_custom_button(__('Complete'), function() {
                frappe.confirm('Please confirm to complete this group class',
                    () => {
                        // action to perform if Yes is selected
                        frappe.call({
                            method: 'club_crm.club_crm.doctype.group_class.group_class.complete_class',
                            args: { group_class_id: frm.doc.name },
                            callback: function(r) {
                                cur_frm.reload_doc();
                            }
                        });
                    }, () => {
                        // action to perform if No is selected
                    })
            }, __("Set"));
        }
        frm.add_custom_button('Group Class Attendees', () => {
            frappe.route_options = { "group_class": frm.doc.name }
            frappe.set_route('List', 'Group Class Attendees');
        }, __("View"));
    }
})