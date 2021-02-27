frappe.listview_settings['Spa Appointment'] = {
	get_indicator: function(doc) {
		var colors = {
            "Draft": "red",
            "Open": "orange",
			"Scheduled": "yellow",
			"Complete": "green",
			"No Show": "grey",
			"Cancelled": "red"
		};
		return [__(doc.appointment_status), colors[doc.appointment_status]];
	}
}; 