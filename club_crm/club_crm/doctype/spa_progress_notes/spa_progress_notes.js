// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Spa Progress Notes', {
	refresh: function(frm) {
		if(!frm.is_new()) {
			frm.add_custom_button(__('Back to Spa Appointment'), function() {
                frappe.set_route("Form", "Spa Appointment", frm.doc.appointment_id);
			});
		}
	}
});
