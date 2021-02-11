// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Check In', {
	on_submit:function(frm){
	    if(frm.doc.check_in_type=="Gym"){
	    var a=0;
	    a=Math.ceil(frm.doc.booked_session-1)
	    if(a<0){
	        a=0;
	    }
     frappe.call({
     "method":"frappe.client.set_value",
     "args":{
         "doctype":"Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "remaining_sessions":frm.doc.remaining_session,
             "used_sessions":frm.doc.used_session,
             "booked_sessions":a
         }
     }
     });
      frappe.call({
     "method":"frappe.client.set_value",
     "args":{
         "doctype":"Fitness Training Appointment",
         "name":frm.doc.gym_booking,
       "fieldname":{
             "status":"Completed"
         }
     }
     });
      }
	}
});
