// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Spa Appointment", "onload", function(frm){
    frm.set_query("client_id", function(){
		return {
			"filters": [["Client", "status", "not in", "Disabled"]]
		}
	});
    frm.set_query("spa_service", function(){
        return {
            "filters": [
                ["Spa Services", "is_addon", "=", "0"],
                ["Spa Services", "enabled", "=", "1"]
            ]
        }
    });
    frm.set_query("session_name", function(){
        return {
            "filters": [
                ["Client Sessions", "client_id", "=", frm.doc.client_id],
                ["Client Sessions", "session_status", "=", "Active"],
                ["Client Sessions", "service_type", "=", "Spa Services"],
            ]
        }
    });
    frm.fields_dict["addon_table"].grid.get_field("addon_service").get_query = function(){
        return {
                filters:{
                        "is_addon": 1
                }
        }
    }
    frm.set_query("club_room", function(){
        return {
            "filters": [
                ["Club Room", "is_group", "=", "0"],
                ["Club Room", "gender_preference", "in", [frm.doc.gender, "Mixed"]]
            ]
        }
    });
    
    // cur_frm.set_query("club_room", function(doc){
    //     return function(callback) {
    //         frappe.call({
    //             method:"club_crm.club_crm.doctype.club_room.club_room.display_service_room",
    //             args: {spa_service: frm.doc.spa_service},
    //             type: "GET",
    //             callback: function(r) {
    //                  var resources = r.message || [];
    //                  callback(resources);
    //             }
    //         })
    //     }
    // });
    
})

frappe.ui.form.on("Spa Appointment", {
    refresh: function(frm) {
        // use the is_new method of frm, to check if the doc is saved or not
        frm.set_df_property("session", "read_only", frm.is_new() ? 0 : 1);
        if (frm.doc.session==0) {
            frm.set_df_property('session_name', 'hidden', 1);
        }
        if(!frm.is_new() && frm.doc.appointment_status == "Open") {
            frappe.call({
                method: 'club_crm.club_crm.doctype.client.client.check_status',
                args: {client_id: frm.doc.client_id},
                callback: function(r) {
                    if (r.message=="Checked-in") {
                        frm.add_custom_button(__('Check In'), function() {
                            frappe.call({
                                method: 'club_crm.club_crm.doctype.check_in.check_in.spa_checkin',
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
                        });
                    }
                }
            });
        }

        if(!frm.is_new() && frm.doc.appointment_status == "Open") {
			frm.add_custom_button(__('No Show'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.spa_appointment.spa_appointment.no_show',
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
			});
		}

        if(frm.doc.payment_status=="Paid" && frm.doc.appointment_status == "Checked-in") {
			frm.add_custom_button(__('Complete'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.spa_appointment.spa_appointment.complete',
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
			});
		}

        if(!frm.is_new() && (frm.doc.appointment_status=="Scheduled" || frm.doc.appointment_status=="Open" || frm.doc.appointment_status=="Draft")) {
			frm.add_custom_button(__('Cancel'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.spa_appointment.spa_appointment.cancel_appointment',
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
			});
		}

        if (frm.doc.appointment_status=="Cancelled" || frm.doc.appointment_status=="No Show") {
			frm.disable_save();
		}

        if (frm.doc.appointment_status=="Checked-in") {
            frappe.call({
                method: 'club_crm.club_crm.doctype.spa_progress_notes.spa_progress_notes.check_if_exists',
                args: {appointment_id: frm.doc.name},
                callback: function(r) {
                    if (r.message==0) {
                        frm.add_custom_button(__('Progress Notes'), function(){
                            let d = new frappe.ui.Dialog({
                                title: 'Progress Notes',
                                fields: [
                                    {
                                        label: 'Notes',
                                        fieldname: 'notes',
                                        fieldtype: 'Small Text',
                                        reqd:1
                                    }
                                ],
                                primary_action_label: ('Submit'), primary_action: function() {
                                    d.hide();
                                    frm.set_value("progress_notes",d.get_value('notes'));
                                    frappe.call({
                                        method: 'club_crm.club_crm.doctype.spa_progress_notes.spa_progress_notes.progress_notes',
                                        args: {appointment_id:frm.doc.name, notes: frm.doc.progress_notes},
                                        callback: function(r) {
                                            cur_frm.reload_doc();
                                        }
                                    });
                                    frappe.msgprint({
                                        title: __('Notification'),
                                        indicator: 'green',
                                        message: __('Progress Notes added successfully')
                                    });
                                 }
                            })
                            d.show();
                        })
                    }
                }
            })
        }

        if(!frm.is_new() && (frm.doc.appointment_status=="Scheduled" || frm.doc.appointment_status=="Open" || frm.doc.appointment_status=="Checked-in") && frm.doc.payment_status=="Not Paid") {
			frm.add_custom_button(__('Add to Cart'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.cart.cart.add_cart_from_spa',
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
			});
		}

        if(!frm.is_new() && frm.doc.payment_status=="Added to cart") {
			frm.add_custom_button(__('Go to Cart'), function() {
                frappe.set_route("Form", "Cart", frm.doc.cart);
			});
		}
    },
    client_id: function(frm) {
        if (frm.doc.session==1) {
            frm.set_df_property('session_name', 'hidden', 0);
        }
        else {
            frm.set_df_property('session_name', 'hidden', 1);
        }
    },
    session: function(frm){
        if (!frm.doc.client_id) {
            frm.set_df_property('session_name', 'hidden', 1);
        }
        frm.set_value("client_id", "");
    }
})