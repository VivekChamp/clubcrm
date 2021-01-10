// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Group Class Scheduler', {
	after_save:function(frm){
	    if(!frm.doc.group_class){
			frm.doc.details.forEach(function(v) {
				frappe.db.insert({
					"doctype" :"Group Class",
					"group_class_name":frm.doc.group_class_name,
	 				"capacity":frm.doc.capacity,
	 				"members_only":frm.doc.members_only,
	 				"show_on_app":frm.doc.show_on_app,
					"trainer":frm.doc.trainer,
					"class_category":frm.doc.group_class_category,
					"class_type":frm.doc.group_class_type,
	 				"from_time":v.start_time,
	 				"to_time":v.to_time,
					"day":v.date
				}).then(vlt=>{
					frappe.model.set_value(frm.doctype, frm.doc.name, 'Group Class', vlt);
					frm.set_value("group_class",vlt.name);
					frappe.show_alert({
						message:__('Group Class {0} Created With filter by ', [vlt.name]),
						indicator:'green'
					});
	     		});
	   		})
	    }
	},

	refresh: function(frm) {
		cur_frm.get_field('group_class_name').get_query = function(doc) {
			return {
				filters: [
					["Group Class Name", "group_class_category", "=", frm.doc.group_class_category]
				   ]
			   };
		   };
		},
});