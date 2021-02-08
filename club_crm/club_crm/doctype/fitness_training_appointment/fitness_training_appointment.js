// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fitness Training Appointment', {
	on_submit:function(frm){
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
},
after_cancel:function(frm){
    if(frm.doc.status=="Scheduled"){
        frm.set_value("booked_sessions",frm.doc.booked_sessions - 1);``
         frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
    }
  if(frm.doc.status!="Scheduled"){
      frm.set_value("used_sessions",frm.doc.used_sessions-1);
      if(frm.doc.used_sessions<0){
          frm.set_value("used_sessions",0);
      }
       frm.set_value("remaining_sessions",Math.ceil(frm.doc.remaining_sessions + 1));
      var a=frm.doc.remaining_sessions+1
      if(frm.doc.number_of_sessions>=a){
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
after_save:function(frm){
               frappe.call({
     "method": "frappe.client.set_value",
     "args":{
         "doctype": "Fitness Training Session",
         "name":frm.doc.fitness_session,
       "fieldname":{
             "booked_sessions":frm.doc.booked_sessions
         }
     }
     });
},
status:function(frm){
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
         }
     }
     });
         }
        frm.set_value("booked_sessions",frm.doc.booked_sessions - 1);
        
        if(frm.doc.booked_sessions<0){
            frm.set_value("booke_sessions","0")
        }
    }
},
})
