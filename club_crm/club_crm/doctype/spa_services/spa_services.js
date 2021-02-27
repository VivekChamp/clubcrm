// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

//Filter in Applicable service for add-ons
cur_frm.set_query("spa_service", "service_for_addon", function(doc) {
	return{
		filters: {'is_addon': '0'}
	}
});

frappe.ui.form.on('Spa Services', {
	// refresh: function(frm) {
	
	// 	}
});