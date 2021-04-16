frappe.listview_settings['Spa Appointment'] = {
	add_fields: ["title", "appointment_status", "service_staff", "appointment_time", "appointment_date"],
	get_indicator: function (doc) {
		if (doc.appointment_status === "Draft") {
			// Draft
			return [__("Draft"), "red", "appointment_status,=,Draft"];
		}
		else if (doc.appointment_status === "Scheduled") {
			// Scheduled
			return [__("Scheduled"), "green", "appointment_status,=,Scheduled"];
		}
		else if (doc.appointment_status === "Open") {
			// Open
			return [__("Open"), "purple", "appointment_status,=,Open"];
		}
		else if (doc.appointment_status === "Checked-in") {
			// Open
			return [__("Checked-in"), "yellow", "appointment_status,=,Checked-in"];
		}
		else if (doc.appointment_status === "Complete") {
			// Complete
			return [__("Complete"), "blue", "appointment_status,=,Complete"];
		}
		else if (doc.appointment_status === "No Show") {
			// No Show
			return [__("No Show"), "light red", "appointment_status,=,No Show"];
		}
		else if (doc.appointment_status === "Cancelled") {
			// Cancelled
			return [__("Cancelled"), "red", "appointment_status,=,Cancelled"];
		}
	}
};
