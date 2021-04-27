// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fitness Training Appointment", "onload", function(frm){
    //Hide disabled clients in Client ID field 
    frm.set_query("client_id", function(){
		return {
			"filters": [["Client", "status", "not in", "Disabled"]]
		}
	});
    // Filter service staff for fitness appointment
    frm.set_query("service_staff", function(){
	    return {
			"filters": [["Service Staff", "fitness_check", "=", "1"]]
		}
	});
    //Filter Session Name based on Client ID, client active session and fitness services
	frm.set_query("session_name", function(){
        return {
            "filters": [
                ["Client Sessions", "client_id", "=", frm.doc.client_id],
                ["Client Sessions", "session_status", "=", "Active"],
                ["Client Sessions", "service_type", "=", "Fitness Services"]
            ]
        }
    });
})

frappe.ui.form.on("Fitness Training Appointment", {
    refresh: function(frm) {
		// use the is_new method of frm, to check if the doc is saved or not
        frm.set_df_property("session", "read_only", frm.is_new() ? 0 : 1);

        // 'Check-in' button for appointment check-in
		if(!frm.is_new() && frm.doc.appointment_status == "Open") {
            frappe.call({
                method: 'club_crm.club_crm.doctype.client.client.check_status',
                args: {client_id: frm.doc.client_id},
                callback: function(r) {
                    if (r.message=="Checked-in") {
                        frm.add_custom_button(__('Check In'), function() {
                            frappe.call({
                                method: 'club_crm.club_crm.doctype.check_in.check_in.fitness_checkin',
                                args: {client_id: frm.doc.client_id, appointment_id:frm.doc.name},
                                callback: function(r) {
                                    cur_frm.reload_doc();
                                }
                            });
                            frappe.msgprint({
                                title: __('Notification'),
                                indicator: 'green',
                                message: __('Checked in successfully')
                            });
                        },__("Set Status"));
                    }
                }
            });
        }

        if(frm.doc.payment_status=="Paid" && frm.doc.appointment_status == "Checked-in") {
			frm.add_custom_button(__('Complete'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.fitness_training_appointment.fitness_training_appointment.complete',
                    args: {appointment_id:frm.doc.name},
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __("Appointment has been marked as 'Completed'")
                });
			},__("Set Status"));
		}

		if(!frm.is_new() && frm.doc.appointment_status == "Open") {
			frm.add_custom_button(__('No Show'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.fitness_training_appointment.fitness_training_appointment.no_show',
                    args: {appointment_id:frm.doc.name},
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __("Appointment has been marked as 'No Show'")
                });
			},__("Set Status"));
		}

		if(!frm.is_new() && (frm.doc.appointment_status=="Scheduled" || frm.doc.appointment_status=="Open" || frm.doc.appointment_status=="Draft")) {
			frm.add_custom_button(__('Cancel'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.fitness_training_appointment.fitness_training_appointment.cancel_appointment',
                    args: {appointment_id:frm.doc.name},
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Appointment has been cancelled')
                });
			},__("Set Status"));
		}

		if (frm.doc.appointment_status=="Cancelled" || frm.doc.appointment_status=="No Show") {
			frm.disable_save();
		}

		if(!frm.is_new() && (frm.doc.appointment_status=="Scheduled" || frm.doc.appointment_status=="Open" || frm.doc.appointment_status=="Checked-in") && frm.doc.payment_status=="Not Paid") {
			frm.add_custom_button(__('To Cart'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.cart.cart.add_cart_from_fitness',
                    args: {client_id: frm.doc.client_id, appointment_id:frm.doc.name},
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Added to cart')
                });
			},__("Add"));
		}

        if(!frm.is_new() && frm.doc.payment_status=="Added to cart") {
			frm.add_custom_button(__('Cart'), function() {
                frappe.set_route("Form", "Cart", frm.doc.cart);
			},__("View"));
		}

          // View Check-in document
          if(frm.doc.checkin_document) {
			frm.add_custom_button(__('Check In'), function() {
                frappe.set_route("Form", "Check In", frm.doc.checkin_document);
			},__("View"));
		}

	}
})

// frappe.ui.form.on("Fitness Training Appointment", {
// 	onload_post_render: function(frm) {
// 		if (!frm.doc.client_id) {
//         	$(frm.fields_dict.session_name.input).on('click', function(e) {
//             // your code goes here
			
// 				frappe.throw(
// 					title='Client not selected',
// 					msg='Please select a client first'
// 				)
//        		});
// 		}
//     }
// })