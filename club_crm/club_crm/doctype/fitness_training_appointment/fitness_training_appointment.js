
// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fitness Training Appointment', {
refresh:function(frm){
        if(frm.doc.status=="Scheduled"){
         var s =frappe.datetime.add_days(frappe.datetime.nowdate())
          if(frm.doc.date==s){
              frm.set_value("status","Open")
            refresh_field("status");
          }
        }
        if(frm.doc.docstatus==1){
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
  },
	 on_submit:function(frm){
	     if(frm.doc.status=="Scheduled"){
	      var s =frappe.datetime.add_days(frappe.datetime.nowdate())
          if(frm.doc.date==s){
              frm.set_value("status"=="Open")
            refresh_field("status");
          }
	     }
      if(frm.doc.status=="Completed"){
     frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "remaining_sessions":frm.doc.remaining_sessions,
             "used_sessions":frm.doc.used_sessions,
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
      }
      if(frm.doc.status=="No show"){
         frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "remaining_sessions":frm.doc.remaining_sessions,
             "used_sessions":frm.doc.used_sessions,
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
         }
	 },
	 after_save:function(frm){
	     if(frm.doc.docstatus<0){
	      if(frm.doc.status=="Scheduled"){
               frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "booked_sessions":frm.doc.booked_sessions,
         }
     }
              
     });
	      }
	      }
	       if(frm.doc.docstatus<0){
	      if(frm.doc.status=="Open"){
	          frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "booked_sessions":frm.doc.booked_sessions,
         }
     }
     });
	      }
	       }
},
after_cancel:function(frm){
    frm.set_value("status","Cancelled")
    if(frm.doc.status=="Scheduled"){
        frm.set_value("booked_sessions",frm.doc.booked_sessions - 1);``
         frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "booked_sessions":frm.doc.booked_sessions,
         }
     }
     });
    }
    if(frm.doc.status=="Open"){
        frm.set_value("booked_sessions",frm.doc.booked_sessions - 1);``
         frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "booked_sessions":frm.doc.booked_sessions,
         }
     }
     });
    }
   if(frm.doc.status=="Completed"){
      frm.set_value("used_sessions",frm.doc.used_sessions-1);
      if(frm.doc.used_sessions<0){
          frm.set_value("used_sessions",0);
      }
       var a=frm.doc.remaining_sessions+1
       frm.set_value("remaining_sessions",a);
      if(frm.doc.number_of_sessions>a){
          frm.set_value("remaining_sessions",0)
      }
  frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "remaining_sessions":frm.doc.remaining_sessions,
             "used_sessions":frm.doc.used_sessions,
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
  }
  if(frm.doc.status=="No show"){
      frm.set_value("used_sessions",frm.doc.used_sessions-1);
      if(frm.doc.used_sessions<0){
          frm.set_value("used_sessions",0);
      }
       var b=frm.doc.remaining_sessions+1
       frm.set_value("remaining_sessions",b);
      if(frm.doc.number_of_sessions>b){
          frm.set_value("remaining_sessions",0)
      }
  frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "remaining_sessions":frm.doc.remaining_sessions,
             "used_sessions":frm.doc.used_sessions,
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
  }
},
	 status:function(frm){
	     if(frm.doc.status=="Completed"){
        frm.set_value("booked_sessions",frm.doc.booked_sessions - 1);
        
        if(frm.doc.booked_sessions<0){
            frm.set_value("booked_sessions","0")
        }
    }
    if(frm.doc.status=="No show"){
        frm.set_value("booked_sessions",frm.doc.booked_sessions - 1);
        
        if(frm.doc.booked_sessions<0){
            frm.set_value("booked_sessions","0")
        }
    }
    if(frm.doc.status=="Completed"){
         if(frm.doc.docstatus==1){
         frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
     "fieldname":{
             "remaining_sessions":frm.doc.remaining_sessions,
             "used_sessions":frm.doc.used_sessions,
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
         }
    }
    if(frm.doc.status=="No show"){
         if(frm.doc.docstatus==1){
         frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "remaining_sessions":frm.doc.remaining_sessions,
             "used_sessions":frm.doc.used_sessions,
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
         }
         }
},
})
