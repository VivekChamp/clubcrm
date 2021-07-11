frappe.listview_settings['Group Class'] = {
    add_fields: ["title", "class_status", "class_date", "remaining"],
    hide_name_column: true,
    get_indicator: function(doc) {
        if (doc.class_status === "Scheduled") {
            // Cart
            return [__("Scheduled"), "green", "class_status,=,Scheduled"];
        } else if (doc.class_status === "Open") {
            // Ordered
            return [__("Open"), "purple", "class_status,=,Open"];
        } else if (doc.class_status === "Completed") {
            // Delivered
            return [__("Completed"), "blue", "class_status,=,Completed"];
        } else if (doc.class_status === "Cancelled") {
            // Cancelled
            return [__("Cancelled"), "red", "class_status,=,Cancelled"];
        }
    }
};