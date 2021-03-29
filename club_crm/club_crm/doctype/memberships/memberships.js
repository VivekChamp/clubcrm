// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Memberships', {
	refresh: function(frm) {
		if (frm.doc.membership_application) {
            frm.add_custom_button(__('Membership Application'), function(){
                frappe.set_route("Form", "Memberships Application", frm.doc.membership_application);
            },__("View"));
        }
        if (frm.doc.membership_application) {
            frm.add_custom_button(__('Active'), function(){
                frappe.call({
                    method: 'club_crm.club_crm.doctype.memberships.memberships.activate_membership',
                    args: {appointment_id: frm.doc.name},
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Membership has been activated')
                });
            },__("Set"));
        }
	}
});