// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Group Class Attendees', {
	refresh: function(frm) {
		if(!frm.is_new() && (frm.doc.class_status=="Open") && frm.doc.docstatus==1) {
			frm.add_custom_button(__('Check-in'), function(){
				frappe.model.open_mapped_doc({
					method: 'club_crm.club_crm.doctype.check_in.check_in.gc_checkin',
					frm: frm,
				});
				frappe.msgprint({
					title: __('Notification'),
					indicator: 'green',
					message: __('Checked in successfully')
				});
			});
		}
	 }
});
