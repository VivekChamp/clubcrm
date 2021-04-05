// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Group Class", "onload", function(frm){
	frm.set_query("group_class_name", function(){
		return {
			"filters": [["Group Class Services", "enabled", "=", 1]]
		}
	});
	frm.set_query("location", function(){
		return {
			"filters": [
				["Club Room", "club_room_type", "=", "Fitness"],
				["Club Room", "is_group", "=", "0"]
			]
		}
	});
	frm.set_query("trainer_name", function(){
		return {
			"filters": [["Service Staff", "fitness_check", "=", 1]]
		}
	});
});