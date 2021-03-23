// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Check In', {
	on_submit: function(frm){
	    if(frm.doc.check_in_type=="Gym"){
        frappe.call({
          "method":"frappe.client.set_value",
          "args": {
          "doctype":"Fitness Training Appointment",
          "name":frm.doc.gym_booking,
          "fieldname":{
            "status":"Completed"
            }
          }
	      });
      }
	},
  refresh: function(frm) {
    if(frm.doc.check_in_type=="Spa") {
			frm.add_custom_button(__('Go to Spa Appointment'), function() {
        frappe.set_route("Form", "Spa Appointment", frm.doc.spa_booking);
			});
		}
    if(frm.doc.check_in_type=="Fitness") {
			frm.add_custom_button(__('Go to Fitness Appointment'), function() {
        frappe.set_route("Form", "Fitness Training Appointment", frm.doc.fitness_booking);
			});
		}
  }
});

