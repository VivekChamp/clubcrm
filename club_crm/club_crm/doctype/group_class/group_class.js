// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Group Class', {
	refresh: function(frm) {
		cur_frm.get_field('group_class_name').get_query = function(doc) {
			return {
				filters: [
					["Group Class Name", "group_class_category", "=", frm.doc.class_category]
				   ]
			   };
		   };
		},
});
