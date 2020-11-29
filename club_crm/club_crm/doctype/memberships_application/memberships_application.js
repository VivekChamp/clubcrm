// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Memberships Application', {
	refresh: function(frm) {
	cur_frm.get_field('membership_plan').get_query = function(doc) {
        return {
            filters: [
                ["Memberships Plan", "membership_type", "=", frm.doc.membership_type]
               ]
           };
	   };
	}
});