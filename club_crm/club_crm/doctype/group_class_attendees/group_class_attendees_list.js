frappe.listview_settings['Group Class Attendees'] = {
    add_fields: ["client_name", "attendee_status", "member_id", "group_class_name", "class_date"],
    hide_name_column: true,
    get_indicator: function(doc) {
        if (doc.attendee_status === "Scheduled") {
            // Cart
            return [__("Scheduled"), "green", "attendee_status,=,Scheduled"];
        } else if (doc.attendee_status === "Open") {
            // Ordered
            return [__("Open"), "purple", "attendee_status,=,Open"];
        } else if (doc.attendee_status === "Waiting List") {
            // Ordered
            return [__("Waiting List"), "orange", "attendee_status,=,Waiting List"];
        } else if (doc.attendee_status === "Checked-in") {
            // Ready
            return [__("Checked-in"), "yellow", "attendee_status,=,Checked-in"];
        } else if (doc.attendee_status === "Complete") {
            // Delivered
            return [__("Complete"), "blue", "attendee_status,=,Complete"];
        } else if (doc.attendee_status === "Cancelled") {
            // Cancelled
            return [__("Cancelled"), "red", "attendee_status,=,Cancelled"];
        } else if (doc.attendee_status === "No Show") {
            // Cancelled
            return [__("No Show"), "red", "attendee_status,=,No Show"];
        }
    }
};