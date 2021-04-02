// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club Packages", "onload", function(frm){
	cur_frm.fields_dict.package_table.grid.get_field("service_type").get_query = function(){
        return {
			filters: [
                ["DocType", "name", "in", ["Spa Services", "Fitness Services", "Club Services"]]
            ]
        }
	}
});
