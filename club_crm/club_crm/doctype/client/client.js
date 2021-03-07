// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client', {
	refresh(frm) {
		frm.add_custom_button(__("Create"), function() {
		    var mem_app = frappe.model.get_new_doc("Memberships Application");
		        mem_app.client=frm.doc.name;
		         frappe.set_route('Form', 'Memberships Application', mem_app.name);
		   },__("Membership Application"));
		
		frm.add_custom_button(__('Accounts Receivable'), function() {
			frappe.set_route('query-report', 'Accounts Receivable', {customer:frm.doc.customer});
		});

		if (frm.doc.status=="Active") {
			frm.add_custom_button(__('Check-in'), function(){
				frappe.call({
					method: 'club_crm.club_crm.doctype.check_in.check_in.club_checkin',
					args: {client_id: frm.doc.name},
					callback: function(r) {
						cur_frm.reload_doc();
					}
				});
				frappe.msgprint({
					title: __('Notification'),
					indicator: 'green',
					message: __('Checked in successfully')
				});
			});
		}

		if (frm.doc.status=="Checked-in") {
		 	frm.add_custom_button(__('Check out'), function(){
				frappe.call({
					method: 'club_crm.club_crm.doctype.check_in.check_in.club_checkout',
					args: {client_id: frm.doc.name},
					callback: function(r) {
						cur_frm.reload_doc();
					}
				});
				frappe.msgprint({
					title: __('Notification'),
					indicator: 'green',
					message: __('Checked out successfully')
				});
		 	});
		}
	}
});

