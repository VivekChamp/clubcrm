// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Sessions", "onload", function(frm){
	frm.set_query("client_id", function(){
		return {
			"filters": [["Client", "status", "not in", "Disabled"]]
		}
	});
	frm.set_query("service_type", function(){
		return {
			"filters": [
				["DocType", "name", "in", ["Spa Services", "Fitness Services", "Club Services"]]
			]
		}
	});
});

frappe.ui.form.on("Client Sessions", {
	onload: function(frm) {
		frm.disable_save();
	},
    refresh(frm) {
		if (frm.doc.session_status=="Expired") {
			frm.set_df_property("session_status", "read_only", 1);
		}

        frm.add_custom_button(__("Extend Validity"), function() {
			let d = new frappe.ui.Dialog ({
				title: 'Extend Validity',
				fields: [
					{
						label: 'Extend the session (from start date) for',
						fieldname: 'extension',
						fieldtype: 'Duration',
						default: frm.doc.expiry_date
					},
					{
						label: 'Reason for extension',
						fieldname: 'extension_reason',
						fieldtype: 'Small Text'
					}
				],
				primary_action_label: ('Submit'),
                primary_action: function() {
                    d.hide(); 
                        frm.set_value('extension', d.get_value('extension'));
						frm.set_value('extension_notes', d.get_value('extension_reason'));
						frm.save();
                }
            });
            d.show();
		});
	},
	start_date: function(frm){
		frm.save();
	},
	used_sessions: function(frm) {
		var remaining = 0;
		if (frm.doc.used_sessions > frm.doc.total_sessions) {
			frappe.throw(__('Number of used sessions cannot be greated than total sessions'))
		}
		else if (frm.doc.used_sessions < 0) {
			frappe.throw(__('Number of used sessions cannot be less than 0'))
		}
		else {
        	remaining = frm.doc.total_sessions - frm.doc.used_sessions;
        	frm.set_value('remaining_sessions', remaining);
		}
	},
	remaining_sessions:function(frm){
		if (frm.doc.remaining_sessions == 0) {
			frm.set_value('session_status', 'Complete');
		}
		else if (frm.doc.remaining_sessions > 0) {
			frm.set_value('session_status', 'Active');
		}
		frm.save()
	}
});