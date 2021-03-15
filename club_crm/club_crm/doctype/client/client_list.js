frappe.listview_settings['Client'] = {
    add_fields: ["full_name", "status", "membership_status", "gender", "mobile_no"],
	get_indicator: function (doc) {
		if (doc.status === "Active") {
			// Active
			return [__("Active"), "green", "status,=,Active"];
		}
		else if (doc.status === "Checked-in") {
			// Checked-in
			return [__("Checked-in"), "blue", "status,=,Checked-in"];
		}
        else if (doc.status === "Disabled") {
			// Disabled
			return [__("Disabled"), "red", "status,=,Disabled"];
		}
    },
    // get_indicator: function (doc) {
	// 	if (doc.membership_status === "Member") {
	// 		// Member
	// 		return [__("Member"), "green", "membership_status,=,Member" ];
	// 	}
	// 	else if (doc.membership_status === "Non-Member") {
	// 		// Non-Member
	// 		return [__("Non-Member"), "blue","membership_status,=,Non-Member"];
	// 	}
    // }
}
        
