frappe.listview_settings['Fitness Training Request'] = {
    add_fields: ["client_name", "request_status", "trainer"],
    get_indicator: function(doc) {
        if (doc.request_status === "Pending") {
            // Draft
            return [__("Pending"), "orange", "request_status,=,Pending"];
        } else if (doc.request_status === "Scheduled") {
            // Scheduled
            return [__("Scheduled"), "green", "request_status,=,Scheduled"];
        } else if (doc.request_status === "Completed") {
            // Complete
            return [__("Completed"), "blue", "request_status,=,Completed"];
        } else if (doc.request_status === "Cancelled") {
            // Cancelled
            return [__("Cancelled"), "red", "request_status,=,Cancelled"];
        }
    }
};