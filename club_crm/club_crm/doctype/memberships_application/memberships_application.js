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
    },

    refresh: function(frm) {
        if(frm.doc.docstatus==1 && frm.doc.payment_status == "Not Paid" && frm.doc.application_status == "Approved"){
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
                  fieldname: 'payment_method',
                  fieldtype: 'Select',
                  options:['Credit Card','Cash'],
                  reqd:1
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
          frm.save('Update');
            frm.set_value("paid_amount",d.get_value('amount'));
            frm.set_value("payment_method",d.get_value('payment_method'));
            frm.set_value("transaction_date",d.get_value('transaction_date'));
            frm.set_value("transaction_reference",d.get_value('transaction_reference'));
            frm.set_value("payment_status","Paid");
         }
        });
        d.show();
      });
      }
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

