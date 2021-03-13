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
    cur_frm.fields_dict["addon_table"].grid.get_field("addon_service").get_query = function(){
        return {
                filters:{
                        "is_addon": 1
                }
        }
    }
    cur_frm.set_query("club_room", function(){
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

        if(!frm.is_new() && (frm.doc.appointment_status=="Checked-in") && frm.doc.payment_status == "Not Paid"){	
			frm.add_custom_button(__('Offline Payment'), function() {	  
						  let d = new frappe.ui.Dialog({
						  title: 'Offline Payment',
						  fields: [
						  {
							  label: 'Transaction Date',
							  fieldname: 'transaction_date',
							  fieldtype: 'Date',
							  default:'Today',
							  read_only:1
						  },
						  {
							  label: 'Paid Amount',
							  fieldname: 'amount',
							  fieldtype: 'Currency',
							  reqd:1
						  },
						  {
							  label: '',
							  fieldname: 'column_break',
							  fieldtype: 'Column Break'
						  },
						  {
							  label: 'Payment Method',
							  fieldname: 'payment_type',
							  fieldtype: 'Select',
							  options:['Credit Card','Cash'],
							  reqd:1
						  },
						  {
							label: 'Card Type',
							fieldname: 'card_type',
							fieldtype: 'Select',
							options:['Visa','MasterCard','Amex','NAPS','CB-Smart'],
							depends_on: 'eval:doc.payment_type=="Credit Card"'
						  },
						  {
							label: 'Transaction Reference #',
							fieldname: 'transaction_reference',
							fieldtype: 'Data',
							depends_on: 'eval:doc.payment_type=="Credit Card"'
						  }
					  		],
				   primary_action_label: ('Submit'),
					 primary_action: function() {
					  d.hide();
					  frm.enable_save();
					  frm.save();
						frm.set_value("paid_amount",d.get_value('amount'));
						frm.set_value("payment_method",d.get_value('payment_type'));
						frm.set_value("card_type",d.get_value('card_type'));
						frm.set_value("transaction_date",d.get_value('transaction_date'));
						frm.set_value("transaction_reference",d.get_value('transaction_reference'));
						frm.set_value("payment_status","Paid");
                        frm.set_value("appointment_status", "Complete")
                        frm.set_value("color", "#20b2aa")
						//frm.set_value("status","Scheduled");
					 }
					});
					d.show();
				  });
				  }
    }
})

// frappe.ui.form.on("Spa Addons", "treatment_duration", function (frm, cdt, cdn) {
//     var total = 0;
//     $.each(frm.doc.addon_table || [], function (i, d) {
//         total += flt(d.treatment_duration);
//     });
//     frm.set_value("addon_total_duration", total);
// });