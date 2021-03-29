frappe.listview_settings['Memberships'] = {
	add_fields: ["title", "membership_status", "membership_id"],
	get_indicator: function (doc) {
		if (doc.membership_status === "Draft") {
			// Draft
			return [__("Draft"), "orange", "membership_status,=,Draft"];
		}
		else if (doc.membership_status === "Active") {
			// Scheduled
			return [__("Active"), "green", "membership_status,=,Active"];
		}
		else if (doc.membership_status === "Expired") {
			// Open
			return [__("Expired"), "red", "membership_status,=,Expired"];
		}
		else if (doc.membership_status === "Frozen") {
			// Open
			return [__("Frozen"), "red", "membership_status,=,Frozen"];
		}
		else if (doc.appointment_status === "Suspended") {
			// Complete
			return [__("Suspended"), "red", "membership_status,=,Suspended"];
		}
		else if (doc.appointment_status === "Cancelled") {
			// No Show
			return [__("Cancelled"), "red", "membership_status,=,Cancelled"];
		}
	}
};
