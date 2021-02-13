// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Check In', {
	on_submit:function(frm){
	    if(frm.doc.check_in_type=="Gym"){
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

