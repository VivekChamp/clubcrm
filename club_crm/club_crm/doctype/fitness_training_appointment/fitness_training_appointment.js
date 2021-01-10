// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fitness Training Appointment', {
	refresh: function(frm) {
		cur_frm.get_field('fitness_session').get_query = function(doc) {
			return {
				filters: [
					["Fitness Training Session", "remaining_sessions", ">", 0]
				   ]
			   };
		   };
		},
});
