// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Group Class Services", "onload", function(frm){
	frm.set_query("group_class_category", function(){
		return {
			"filters": [["Group Class Services Category", "enabled", "=", 1]]
		}
	});
});