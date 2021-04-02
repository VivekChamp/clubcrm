// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Memberships", "onload", function(frm){
    // Filter service staff for fitness appointment
    frm.set_query("assigned_to_1", function(){
	    return {
			"filters": [["Service Staff", "cec_check", "=", "1"]]
		}
	});
    frm.set_query("assigned_to_2", function(){
	    return {
			"filters": [["Service Staff", "cec_check", "=", "1"]]
		}
	});
    frm.fields_dict.additional_members_item.grid.get_field("assigned_to").get_query = function(){
        return {
			filters: [["Service Staff", "cec_check", "=", "1"]]
        }
	}
});

frappe.ui.form.on('Memberships', {
	refresh: function(frm) {
		if (frm.doc.membership_application) {
            frm.add_custom_button(__('Membership Application'), function(){
                frappe.set_route("Form", "Memberships Application", frm.doc.membership_application);
            },__("View"));
        }
        if (frm.doc.membership_application && frm.doc.membership_status=="Draft") {
            frm.add_custom_button(__('Active'), function(){
                frappe.call({
                    method: 'club_crm.club_crm.doctype.memberships.memberships.activate_membership',
                    args: {appointment_id: frm.doc.name},
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Membership has been activated')
                });
            },__("Set"));
        }
	}
});