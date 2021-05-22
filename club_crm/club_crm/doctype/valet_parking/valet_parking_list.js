frappe.listview_settings['Valet Parking'] = {
    add_fields: ["client_name", "date", "status", "member_id"],
    get_indicator: function(doc) {
        if (doc.status === "Parked") {
            // Draft
            return [__("Parked"), "orange", "status,=,Parked"];
        } else if (doc.status === "Requested for Delivery") {
            // Scheduled
            return [__("Requested for Delivery"), "red", "status,=,Requested for Delivery"];
        } else if (doc.status === "Ready for Delivery") {
            // Complete
            return [__("Ready for Delivery"), "green", "status,=,Ready for Delivery"];
        } else if (doc.status === "Delivered") {
            // Cancelled
            return [__("Delivered"), "blue", "request_status,=,Delivered"];
        }
    }
};