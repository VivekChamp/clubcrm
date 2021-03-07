frappe.listview_settings['Spa Appointment'] = {
	add_fields: ["title", "appointment_status", "spa_therapist", "appointment_time", "appointment_date"],
	get_indicator: function (doc) {
		if (doc.appointment_status === "Draft") {
			// Draft
			return [__("Draft"), "red", "appointment_status,=,Draft"];
		}
		else if (doc.appointment_status === "Scheduled") {
			// Scheduled
			return [__("Scheduled"), "yellow", "appointment_status,=,Scheduled"];
		}
		else if (doc.appointment_status === "Open") {
			// Open
			return [__("Open"), "orange", "appointment_status,=,Open"];
		}
		else if (doc.appointment_status === "Checked-in") {
			// Open
			return [__("Checked-in"), "lightblue", "appointment_status,=,Checked-in"];
		}
		else if (doc.appointment_status === "Complete") {
			// Complete
			return [__("Complete"), "green", "appointment_status,=,Complete"];
		}
		else if (doc.appointment_status === "No Show") {
			// No Show
			return [__("No Show"), "grey", "appointment_status,=,No Show"];
		}
		else if (doc.appointment_status === "Cancelled") {
			// Cancelled
			return [__("Cancelled"), "red", "appointment_status,=,Cancelled"];
		}
	}
};
