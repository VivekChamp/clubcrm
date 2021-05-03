// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Memberships", "onload", function(frm) {
    // Filter service staff for fitness appointment
    frm.set_query("assigned_to_1", function() {
        return {
            "filters": [
                ["Service Staff", "cec_check", "=", "1"]
            ]
        }
    });
    frm.set_query("assigned_to_2", function() {
        return {
            "filters": [
                ["Service Staff", "cec_check", "=", "1"]
            ]
        }
    });
    frm.fields_dict.additional_members_item.grid.get_field("assigned_to").get_query = function() {
        return {
            filters: [
                ["Service Staff", "cec_check", "=", "1"]
            ]
        }
    }
});

frappe.ui.form.on('Memberships', {
    refresh: function(frm) {
        frm.fields_dict['validity_extension'].grid.wrapper.find('.grid-add-row').hide();
        if (frm.doc.membership_application) {
            frm.add_custom_button(__('Membership Application'), function() {
                frappe.set_route("Form", "Memberships Application", frm.doc.membership_application);
            }, __("View"));
        }
        frm.add_custom_button('Benefit Sessions', () => {
            frappe.route_options = { "membership_no": frm.doc.name }
            frappe.set_route('List', 'Client Sessions');
        }, __("View"));

        //if (frm.doc.membership_application && frm.doc.membership_status=="Draft") {
        if (frm.doc.membership_status == "Draft" || frm.doc.membership_status == "Cancelled") {
            frm.add_custom_button(__('Active'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.memberships.memberships.activate_membership',
                    args: { appointment_id: frm.doc.name },
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                // frappe.msgprint({
                //     title: __('Notification'),
                //     indicator: 'green',
                //     message: __('Membership has been activated')
                // });
            }, __("Set"));
        }
        if (frm.doc.membership_status == "Active") {
            frm.add_custom_button(__('Cancel'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.memberships.memberships.cancel_membership',
                    args: { appointment_id: frm.doc.name },
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'red',
                    message: __('Membership has been cancelled')
                });
            });
        }
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
                        label: 'Extend the membership validity for',
                        fieldname: 'extension',
                        fieldtype: 'Duration',
                        "hide_seconds": 1,
                        "hide_minute": 1,
                        "hide_hour": 1,
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
                    let row = frappe.model.add_child(frm.doc, 'Validity Extension', 'validity_extension');
                    frappe.model.set_value(row.doctype, row.name, 'entry_date', d.get_value('entry_date'));
                    frappe.model.set_value(row.doctype, row.name, 'days', d.get_value('extension'));
                    frappe.model.set_value(row.doctype, row.name, 'notes', d.get_value('extension_reason'));
                }
            });
            d.show();
        });

        // frm.add_custom_button(__("Renew Membership"), function() {
        //     frappe.model.open_mapped_doc({
        //         method: 'club_crm.club_crm.doctype.memberships_application.memberships_application.renew_membership_single',
        //         frm: frm,
        //     });
        // });
    }
});