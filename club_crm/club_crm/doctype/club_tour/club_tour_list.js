frappe.listview_settings['Club Tour'] = {
    add_fields: ["client_name", "tour_status", "start_time"],
    get_indicator: function(doc) {
        if (doc.tour_status === "Pending") {
            // Pending
            return [__("Pending"), "orange", "tour_status,=,Pending"];
        } else if (doc.tour_status === "Scheduled") {
            // Scheduled
            return [__("Scheduled"), "green", "tour_status,=,Scheduled"];
        } else if (doc.tour_status === "Completed") {
            // Completed
            return [__("Completed"), "blue", "tour_status,=,Completed"];
        } else if (doc.tour_status === "No Show") {
            // No Show
            return [__("No Show"), "red", "tour_status,=,No Show"];
        } else if (doc.tour_status === "Cancelled") {
            // Cancelled
            return [__("Cancelled"), "red", "tour_status,=,Cancelled"];
        }
    }
}