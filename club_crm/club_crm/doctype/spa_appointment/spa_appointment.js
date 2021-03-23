// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Spa Appointment", "onload", function(frm){
    //Hide disabled clients in Client ID field 
    frm.set_query("client_id", function(){
		return {
			"filters": [["Client", "status", "not in", "Disabled"]]
		}
	});
    //Filter Spa Services based on Add-on service check
    frm.set_query("spa_service", function(){
        if (frm.doc.addon_service_check==0) {
            return {
                "filters": [
                    ["Spa Services", "is_addon", "=", "0"],
                    ["Spa Services", "enabled", "=", "1"]
                ]
            }
        }
        else if (frm.doc.addon_service_check==1) {
            return {
                "filters": [
                    ["Spa Services", "is_addon", "=", "1"],
                    ["Spa Services", "enabled", "=", "1"]
                ]
            }
        }
    });
    //Filter Session Name based on Client ID, client active session and spa services
    frm.set_query("session_name", function(){
        return {
            "filters": [
                ["Client Sessions", "client_id", "=", frm.doc.client_id],
                ["Client Sessions", "session_status", "=", "Active"],
                ["Client Sessions", "service_type", "=", "Spa Services"],
                ["Client Sessions", "remaining_sessions", "!=", 0]
            ]
        }
    });
    //Filter add-on table for add-on services only
    frm.fields_dict["addon_table"].grid.get_field("addon_service").get_query = function(){
        return {
                filters:{
                        "is_addon": 1
                }
        }
    }
    //Filter club-room based on client gender
    frm.set_query("club_room", function(){
        return {
            "filters": [
                ["Club Room", "is_group", "=", "0"],
                ["Club Room", "gender_preference", "in", [frm.doc.gender, "Mixed"]]
            ]
        }
    });
    // frm.set_query("club_room", function(doc){
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

        // 'Check-in' button for appointment check-in
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
                                    frm.reload_doc();
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

        // 'Complete' button to mark the appointment as complete
        if(frm.doc.appointment_status == "Checked-in") {
			frm.add_custom_button(__('Complete'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.spa_appointment.spa_appointment.complete',
                    args: {appointment_id:frm.doc.name},
                    callback: function(r) {
                        frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __("Appointment has been marked as 'Completed'")
                });
			},__("Set Status"));
		}

        // 'No Show' button for client no-shows.
        if(!frm.is_new() && frm.doc.appointment_status == "Open") {
			frm.add_custom_button(__('No Show'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.spa_appointment.spa_appointment.no_show',
                    args: {appointment_id:frm.doc.name},
                    callback: function(r) {
                        frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __("Appointment has been marked as 'No Show'")
                });
			},__("Set Status"));
		}

        // 'Cancel' button for cancelling appointment
        if(!frm.is_new() && (frm.doc.appointment_status=="Scheduled" || frm.doc.appointment_status=="Open" || frm.doc.appointment_status=="Draft")) {
			frm.add_custom_button(__('Cancel'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.spa_appointment.spa_appointment.cancel_appointment',
                    args: {appointment_id:frm.doc.name},
                    callback: function(r) {
                        frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Appointment has been cancelled')
                });
			},__("Set Status"));
		}

        // Disable save for cancelled and no-show appointments
        if (frm.doc.appointment_status=="Cancelled" || frm.doc.appointment_status=="No Show") {
			frm.disable_save();
		}

        // Add progress notes for appointment
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
                        },__("Add"))
                    }
                }
            })
        }

        // Add to cart
        if(!frm.is_new() && (frm.doc.appointment_status=="Scheduled" || frm.doc.appointment_status=="Open" || frm.doc.appointment_status=="Checked-in") && frm.doc.payment_status=="Not Paid") {
			frm.add_custom_button(__('To Cart'), function() {
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
			},__("Add"));
		}

        // View Cart
        if(!frm.is_new() && (frm.doc.payment_status=="Added to cart" || frm.doc.payment_status=="Paid")) {
			frm.add_custom_button(__('Cart'), function() {
                frappe.set_route("Form", "Cart", frm.doc.cart);
			},__("View"));
		}

        // View progress notes document
        if(frm.doc.progress_notes_id) {
			frm.add_custom_button(__('Progress Notes'), function() {
                frappe.set_route("Form", "Spa Progress Notes", frm.doc.progress_notes_id);
			},__("View"));
		}

        // View Check-in document
        if(frm.doc.checkin_document) {
			frm.add_custom_button(__('Check In'), function() {
                frappe.set_route("Form", "Check In", frm.doc.checkin_document);
			},__("View"));
		}
        
    }
});