frappe.listview_settings['Client'] = {
    add_fields: ["full_name", "membership_status", "member_id", "assigned_cec", "gender"],
    hide_name_column: true,
    // get_indicator: function (doc) {
    // 	if (doc.membership_status === "Member" && doc.status === "Active") {
    // 		// Member
    // 		return [__("Member"), "green", "membership_status,=,Member" ];
    // 	}
    // 	else if (doc.membership_status === "Non-Member") {
    // 		// Non-Member
    // 		return [__("Non-Member"), "blue","membership_status,=,Non-Member"];
    // 	}
    // }
    get_indicator: function(doc) {
            if (doc.membership_status === "Member") {
                // Member
                return [__("Member"), "green", "membership_status,=,Member"];
            } else if (doc.membership_status === "Non-Member") {
                // Non-Member
                return [__("Non-Member"), "blue", "membership_status,=,Non-Member"];
            }
        }
        // onload: function(listview) {
        //     listview.page.add_inner_button(__("Clear Error Logs"), function() {
        //         frappe.call({
        //             method: 'frappe.core.doctype.error_log.error_log.clear_error_logs',
        //             callback: function() {
        //                 listview.refresh();
        //             }
        //         });
        //     });
        // }
}