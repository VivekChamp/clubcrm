// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Memberships Application', {
	refresh: function(frm) {
	cur_frm.get_field('membership_plan').get_query = function(doc) {
        return {
            filters: [
                ["Memberships Plan", "membership_type", "=", frm.doc.membership_type]
               ]
           };
       };



	}
});

// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Memberships Application', {
// 	refresh: function(frm) {
// 		if (frm.doc.docstatus == 1 && frm.doc.application_status == "Approved"){
// 		cur_frm.add_custom_button(__("Make Offline Payment"), function() {

// 			let d = new frappe.ui.Dialog({
// 			title: 'Enter payment details',
// 			fields: [
//         		{
//            		label: 'Payment Method',
//             	fieldname: 'payment_method',
//             	fieldtype: 'Select',
// 				options: [ 'Cash','Card']
// 				}
				
// 			],
//     		primary_action: function(){
//        		d.hide();
//         	show_alert(d.get_values());
//             }
            


//         });
//         d.show()
// 		});
//     }
// }
// });

