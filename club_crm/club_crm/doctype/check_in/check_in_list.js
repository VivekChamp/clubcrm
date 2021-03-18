frappe.listview_settings['Check In'] = {
	add_fields: ["client_name", "check_in_type", "check_in_time"],
	get_indicator: function (doc) {
		if (doc.check_in_type === "Club Check-in") {
			// Draft
			return [__("Club Check-in"), "purple", "check_in_type,=,Club Check-in"];
		}
        else if (doc.check_in_type === "Spa") {
			// Draft
			return [__("Spa"), "blue", "check_in_type,=,Spa"];
        }
        else if (doc.check_in_type === "Gym") {
			// Draft
			return [__("Gym"), "blue", "check_in_type,=,Gym"];
        }
        else if (doc.check_in_type === "Group Class") {
			// Draft
			return [__("Group Class"), "blue", "check_in_type,=,Group Class"];
        }
	}
};