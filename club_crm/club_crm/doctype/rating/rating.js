// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rating', {
	refresh:function(frm) {
		frm.set_query('rating_type',function() {
			return {
				filters: {
					'name':['in',['Spa Appointment', 'Group Class']]
				}
			}
		});
	}
});