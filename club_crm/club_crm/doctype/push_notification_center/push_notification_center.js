// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Push Notification Center', {
	onload: function(frm) {
			frm.disable_save();
	},
  send_to: function(frm){
        frm.set_value('client_id', "");
		frm.set_value('client_name', "");
    }
});