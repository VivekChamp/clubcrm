// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Sessions", "onload", function(frm) {
    frm.set_query("client_id", function() {
        return {
            "filters": [
                ["Client", "status", "not in", "Disabled"]
            ]
        }
    });
    frm.set_query("service_type", function() {
        return {
            "filters": [
                ["DocType", "name", "in", ["Spa Services", "Fitness Services", "Club Services"]]
            ]
        }
    });
});

frappe.ui.form.on("Client Sessions", {
    refresh(frm) {
        frm.fields_dict['session_extension'].grid.wrapper.find('.grid-add-row').hide();
        frm.add_custom_button(__("View Appointments"), function() {
            if (frm.doc.service_type == "Fitness Services") {
                frappe.route_options = { "session_name": frm.doc.name }
                frappe.set_route('List', 'Fitness Training Appointment');
            }
            if (frm.doc.service_type == "Spa Services") {
                frappe.route_options = { "session_name": frm.doc.name }
                frappe.set_route('List', 'Spa Appointment');
            }
        })
        if (frm.doc.is_benefit == 0 && !in_list(frappe.user_roles, "Fitness Trainer")) {
            frm.add_custom_button(__("Extend Validity"), function() {
                let d = new frappe.ui.Dialog({
                    title: 'Extend Validity',
                    fields: [{
                            label: 'Entry Date',
                            fieldname: 'entry_date',
                            fieldtype: 'Date',
                            default: 'Today',
                            read_only: 1
                        },
                        {
                            label: 'Extend the session validity for',
                            fieldname: 'extension',
                            fieldtype: 'Duration',
                            "hide_seconds": 1,
                            reqd: 1
                        },
                        {
                            label: 'Reason for extension',
                            fieldname: 'extension_reason',
                            fieldtype: 'Small Text',
                            reqd: 1
                        }
                    ],
                    primary_action_label: ('Submit'),
                    primary_action: function() {
                        d.hide();
                        frm.save();
                        let row = frappe.model.add_child(frm.doc, 'Validity Extension', 'session_extension');
                        frappe.model.set_value(row.doctype, row.name, 'entry_date', d.get_value('entry_date'));
                        frappe.model.set_value(row.doctype, row.name, 'days', d.get_value('extension'));
                        frappe.model.set_value(row.doctype, row.name, 'notes', d.get_value('extension_reason'));
                    }
                });
                d.show();
            });
        }
    },
    start_date: function(frm) {
        frm.save();
    },
    used_sessions: function(frm) {
        var remaining = 0;
        if (frm.doc.used_sessions > frm.doc.total_sessions) {
            frappe.throw(__('Number of used sessions cannot be greated than total sessions'))
        } else if (frm.doc.used_sessions < 0) {
            frappe.throw(__('Number of used sessions cannot be less than 0'))
        } else {
            remaining = frm.doc.total_sessions - frm.doc.used_sessions;
            frm.set_value('remaining_sessions', remaining);
        }
    },
    remaining_sessions: function(frm) {
        if (frm.doc.remaining_sessions == 0) {
            frm.set_value('session_status', 'Complete');
        } else if (frm.doc.remaining_sessions > 0) {
            frm.set_value('session_status', 'Active');
        }
        frm.save()
    }
});