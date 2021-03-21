// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fitness Services', {
	refresh: function(frm) {
		cur_frm.get_field('fitness_category').get_query = function(doc) {
			return {
				filters: [
					["Fitness Services Category", "enabled", "=", "1"]
				   ]
			   };
		   };
		}
});
