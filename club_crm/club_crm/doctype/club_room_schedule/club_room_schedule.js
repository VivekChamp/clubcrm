// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Club Room Schedule', {
	refresh: function(frm) {
		cur_frm.get_field('room_name').get_query = function(doc) {
			return {
				filters: [
					["Club Room", "parent_club_room", "in", ["Male Room","Female Room","Fitness Rooms"]]
				   ]
			   };
		   };
		}
});
