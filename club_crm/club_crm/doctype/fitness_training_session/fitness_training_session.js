// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fitness Training Session', {

    refresh: function(frm) {
        if(frm.doc.docstatus==1 && frm.doc.payment_status == "Not Paid"){
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
				label: 'Card Type',
				fieldname: 'card_type',
				fieldtype: 'Select',
				options:['Visa','MasterCard','Amex','NAPS','CB-Smart'],
                depends_on: 'eval:doc.payment_method=="Credit Card"',
                reqd:1
			  },
              {
                  label: 'Transaction Reference #',
                  fieldname: 'transaction_reference',
                  fieldtype: 'Data',
                  depends_on: 'eval:doc.payment_method=="Credit Card"'
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
			frm.set_value("session_status","Active");
         }
        });
        d.show();
      });
      }

      if (frm.doc.session_status=="Active" && frm.doc.remaining_sessions > 0) {
        frm.add_custom_button(__('Book Appointment'), function(){
            frappe.model.open_mapped_doc({
                method: 'club_crm.club_crm.doctype.fitness_training_appointment.fitness_training_appointment.book_appointment',
                frm: frm,
            });
        });
      }
    }
});
