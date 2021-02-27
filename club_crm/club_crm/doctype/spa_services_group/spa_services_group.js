// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Spa Services Group', {
	refresh: function(frm) {
		cur_frm.get_field('spa_category').get_query = function(doc) {
			return {
				filters: [
					["Spa Services Category", "enabled", "=", "1"]
				   ]
			   };
		   };
		}
});