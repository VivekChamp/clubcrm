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
				["DocType", "name", "in", ["Spa Services", "Fitness Services"]]
			]
		}
	});
	frm.set_query("service_name", function(){
		if(frm.doc.session_type == "Spa Services"){
			return {
				"filters": [
					["Spa Services", "session_type", "in", "Multiple"]
				]
			}
		}
	});
});

frappe.ui.form.on("Client Sessions", {
    refresh(frm) {
		if(frm.doc.docstatus==1) {
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
                            // let row = frappe.model.add_child(frm.doc, 'Cart Payment', 'payment_table'); 
                            frm.set_value('extension', d.get_value('extension'));
							frm.set_value('extension_notes', d.get_value('extension_reason'));
							frm.save('Update');
                            //frappe.model.set_value(row.doctype, row.name, 'paid_amount', d.get_value('amount_paid')); 
                        }
                    });
                d.show();
			});
		}
	},
	start_date: function(frm){
		frm.save('Update');
		frm.refresh_field('session_status');
	}
	// session_status: function(frm){
	// 	frm.refresh_field('session_status');
	// }
});