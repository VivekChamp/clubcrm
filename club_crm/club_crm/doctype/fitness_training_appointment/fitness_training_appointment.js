// For license information, please see license.txt

frappe.ui.form.on('Fitness Training Appointment', {
    refresh: function(frm) {
		if(frm.doc.status=="Open"){
			frm.add_custom_button('Check In',function(){
			   frappe.route_options = {
			  "client_id":frm.doc.client_id,
			  "check_in_type":"Gym",
			  "check_in_time":frm.doc.start_time,
			  "check_out_time":frm.doc.end_time,
			  "gym_booking":frm.doc.name,
			  "used_session":frm.doc.used_sessions,
		 };
		 frappe.new_doc("Check In");
					});
			 }
    }
    })
