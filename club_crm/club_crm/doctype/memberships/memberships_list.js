frappe.listview_settings['Memberships'] = {
	add_fields: ["title", "membership_status", "membership_id"],
	get_indicator: function (doc) {
		if (doc.membership_status === "Draft") {
			return [__("Draft"), "orange", "membership_status,=,Draft"];
		}
		else if (doc.membership_status === "Active") {
			return [__("Active"), "green", "membership_status,=,Active"];
		}
		else if (doc.membership_status === "Expired") {
			return [__("Expired"), "red", "membership_status,=,Expired"];
		}
		else if (doc.membership_status === "Frozen") {
			return [__("Frozen"), "orange", "membership_status,=,Frozen"];
		}
		else if (doc.membership_status === "Suspended") {
			return [__("Suspended"), "red", "membership_status,=,Suspended"];
		}
		else if (doc.membership_status === "Cancelled") {
			return [__("Cancelled"), "red", "membership_status,=,Cancelled"];
		}
	}
};
