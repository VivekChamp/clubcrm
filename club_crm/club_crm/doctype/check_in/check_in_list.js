frappe.listview_settings['Check In'] = {
    add_fields: ["client_name", "member_id", "check_in_type", "check_in_time"],
    hide_name_column: true,
    get_indicator: function(doc) {
        if (doc.check_in_type === "Club Check-in") {
            // Draft
            return [__("Club Check-in"), "purple", "check_in_type,=,Club Check-in"];
        } else if (doc.check_in_type === "Spa") {
            // Draft
            return [__("Spa"), "yellow", "check_in_type,=,Spa"];
        } else if (doc.check_in_type === "Fitness") {
            // Draft
            return [__("Fitness"), "blue", "check_in_type,=,Fitness"];
        } else if (doc.check_in_type === "Group Class") {
            // Draft
            return [__("Group Class"), "green", "check_in_type,=,Group Class"];
        }
    }
};