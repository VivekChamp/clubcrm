frappe.listview_settings['Client Sessions'] = {
    add_fields: ['title', 'package_name', 'remaining_session_text', 'session_status', 'member_id'],
    hide_name_column: true,
    get_indicator: function(doc) {
        if (doc.session_status === "Draft") {
            return [__("Draft"), "orange", "session_status,=,Draft"];
        } else if (doc.session_status === "Active") {
            return [__("Active"), "green", "session_status,=,Active"];
        } else if (doc.session_status === "Expired") {
            return [__("Expired"), "red", "session_status,=,Expired"];
        } else if (doc.session_status === "Cancelled") {
            return [__("Cancelled"), "red", "session_status,=,Cancelled"];
        } else if (doc.session_status === "Complete") {
            return [__("Complete"), "blue", "session_status,=,Complete"];
        } else if (doc.session_status === "On Hold") {
            return [__("On Hold"), "orange", "session_status,=,On Hold"];
        }
    }
};