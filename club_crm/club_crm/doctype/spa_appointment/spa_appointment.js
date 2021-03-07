// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Spa Appointment", "onload", function(frm){
    cur_frm.set_query("spa_service", function(){
        return {
            "filters": [
                ["Spa Services", "is_addon", "=", "0"],
                ["Spa Services", "enabled", "=", "1"]
            ]
        }
    });
    // cur_frm.set_query("addon_table","addon_service", function(){
    //         return {
    //             "filters" : {
    //                 "is_addon": 1,
    //                 "enabled": 1
    //             }
    //         }
    //     });
})

// frappe.ui.form.on('Spa Addons', {
// 	refresh(frm) {
// 	    cur_frm.set_query("addon_service", function(){
//         return {
//             "filters": [
//                 ["Spa Services", "is_addon", "=", "1"]
//             ]
//         }
//     });
// 	}
// })

frappe.ui.form.on("Spa Appointment", {
    refresh: function(frm) {
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

        if (frm.doc.appointment_status=="Cancelled") {
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

    }
})

// frappe.ui.form.on("Spa Addons", {
//     onload: function(frm){
//         frm.set_query("addon_service", function(){
//             return {
//                 "filters": {
//                     "is_addon": 1
//                 }
//             }
//         });
//     }
// })

// frappe.ui.form.on("Spa Addons", "treatment_duration", function (frm, cdt, cdn) {
//     var total = 0;
//     $.each(frm.doc.addon_table || [], function (i, d) {
//         total += flt(d.treatment_duration);
//     });
//     frm.set_value("addon_total_duration", total);
// });