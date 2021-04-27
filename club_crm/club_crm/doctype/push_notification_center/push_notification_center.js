// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Push Notification Center', {
	onload: function(frm) {
			frm.disable_save();
	},
  	send_to: function(frm){
        frm.set_value('client_id', "");
		frm.set_value('client_name', "");
    },
	refresh: function(frm) {
		frm.add_custom_button(__('Send Notification'), function(){
			frappe.call({
				method: 'club_crm.club_crm.doctype.push_notification_center.push_notification_center.send_push_notification',
				args: {client_id: frm.doc.client_id, title: frm.doc.title, message: frm.doc.message},
				callback: function(r) {
					cur_frm.reload_doc();
				}
			});
			// frappe.msgprint({
			// 	title: __('Notification'),
			// 	indicator: 'green',
			// 	message: __('Push Notification sent successfully')
			// });	
		});
	}
});