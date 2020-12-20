// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Restaurant Food Menu', {
	setup: function(frm) {
		frm.add_fetch('item', 'standard_rate', 'rate');
	},
});
