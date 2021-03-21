frappe.listview_settings['Cart'] = {
	add_fields: ["client_name", "payment_status", "date", "grand_total"],
	get_indicator: function (doc) {
		if (doc.payment_status === "Not Paid") {
			// Draft
			return [__("Not Paid"), "red", "status,=,Not Paid"];
		}
        else if (doc.payment_status === "Paid") {
			// Draft
			return [__("Paid"), "green", "status,=,Paid"];
		}
        else if (doc.payment_status === "Cancelled") {
			// Draft
			return [__("Cancelled"), "orange", "status,=,Cancelled"];
		}
	}
};