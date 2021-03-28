frappe.listview_settings['Client Sessions'] = {
	add_fields: ["title", "session_status", "remaining_session_text"],
    // colwidths: {"title": 4, 'session_status':2, "used_sessions": 1, "remaining_sessions":1, "booked_sessions":1},
	get_indicator: function (doc) {
		if (doc.session_status === "Active") {
			return [__("Active"), "green", "session_status,=,Active"];
		}
        else if (doc.session_status === "Expired") {
			// Draft
			return [__("Expired"), "red", "session_status,=,Paid"];
		}
        else if (doc.session_status === "Complete") {
			// Draft
			return [__("Complete"), "blue", "session_status,=,Complete"];
		}
        else if (doc.session_status === "On Hold") {
			// Draft
			return [__("On Hold"), "orange", "session_status,=,On Hold"];
		}
	}
};