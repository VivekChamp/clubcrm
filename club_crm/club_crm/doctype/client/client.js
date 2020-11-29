// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client', {
	refresh(frm) {
		frm.add_custom_button(__("Create"), function() {
		    var mem_app = frappe.model.get_new_doc("Memberships Application");
		        mem_app.client=frm.doc.name;
		         frappe.set_route('Form', 'Memberships Application', mem_app.name);
		   },__("Membership Application"));
	}
});