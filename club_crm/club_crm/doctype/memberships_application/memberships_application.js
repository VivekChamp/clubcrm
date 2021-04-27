// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Memberships Application", "onload", function(frm){
    frm.set_query("membership_plan", function(){
		return {
			"filters": {
                "membership_category" : frm.doc.membership_category
            }
		}
	});
    frm.set_query("assigned_to", function(){
		return {
			"filters": [["Service Staff", "cec_check", "=", "1"]]
		}
	});
});

frappe.ui.form.on('Memberships Application', {
    membership_category: function(frm){
        frm.set_value('membership_plan', "");
    },
    birth_date_1: function(frm) {
        var today = new Date();
        var birthDate = new Date(frm.doc.birth_date_1);
        var age = today.getFullYear() - birthDate.getFullYear();
        var m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) 
        {
            age--;
        }
        if (age > 18) {
            frm.set_value('no_of_adults', 1);
        }
        else {
            frappe.throw(__('The applicant is below 18 years of age.'))
        }
    },
    birth_date_2: function(frm) {
        var today = new Date();
        var birthDate = new Date(frm.doc.birth_date_2);
        var age = today.getFullYear() - birthDate.getFullYear();
        var m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) 
        {
            age--;
        }
        if (age > 18) {
            frm.set_value('no_of_adults', 2);
        }
        else {
            frappe.throw(__('The applicant is below 18 years of age.'))
        }
    },
    discount_type: function(frm) {
        frm.set_value('discount_percentage', 0.0);
        frm.set_value('discount_amount', 0.0);
    },
    apply_discount: function(frm) {
        frm.set_value('discount_percentage', 0.0);
    },
    discount_amount: function(frm) {
        var grand_total = 0.0;
        grand_total = frm.doc.net_total - frm.doc.discount_amount;
        frm.set_value('grand_total', grand_total);
    },
    discount_percentage: function(frm) {
        var discount_amount = 0.0;
        if (frm.doc.apply_discount=="On Joining Fee") {
            discount_amount =  (frm.doc.joining_fee * frm.doc.discount_percentage) / 100;
        }
        else if (frm.doc.apply_discount=="On Membership Fee (Adult)") {
            discount_amount =  (frm.doc.membership_fee_adult * frm.doc.discount_percentage) / 100;
        }
        else if (frm.doc.apply_discount=="On Membership Fee (Child)") {
            discount_amount =  (frm.doc.membership_fee_child * frm.doc.discount_percentage) / 100;
        }
        else if (frm.doc.apply_discount=="On Total Membership Fee") {
            discount_amount =  (frm.doc.total_membership_fee * frm.doc.discount_percentage) / 100;
        }
        else if (frm.doc.apply_discount=="On Net Total") {
            discount_amount =  (frm.doc.net_total * frm.doc.discount_percentage) / 100;
        }
        frm.set_value('discount_amount', discount_amount);
    },
    grand_total: function(frm){
        frm.set_value('total_to_be_paid', frm.doc.grand_total);
    },
    total_to_be_paid:function(frm){
        frm.set_value('balance_amount', frm.doc.total_to_be_paid - frm.doc.paid_amount); 
    },
    balance_amount:function(frm){
        if (frm.doc.balance_amount==0.0) {
            frm.set_value('payment_status', 'Paid');
        }
    },
    refresh: function(frm) {
        //Hide Buttons on Child Table
        frm.fields_dict['membership_payment'].grid.wrapper.find('.grid-add-row').hide();
        if (frm.doc.payment_status=="Paid") {
            frm.fields_dict['membership_payment'].grid.wrapper.find('.grid-remove-rows').hide();
        }
        //Show payment button
        if(frm.doc.workflow_status=="Approved by MD" && !frm.doc.balance_amount==0.0) {
            frm.add_custom_button(__('Offline Payment'), function() {
                let d = new frappe.ui.Dialog ({
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
                            label: 'Total Amount to Pay',
                            fieldname: 'amount_to_pay',
                            fieldtype: 'Currency',
                            default: frm.doc.total_to_be_paid,
                            read_only:1
                        },
                        {
                            label: 'Total Amount Paid',
                            fieldname: 'total_amount_paid',
                            fieldtype: 'Currency',
                            default: frm.doc.paid_amount,
                            read_only:1
                        },
                        {
                            label: 'Balance to Pay',
                            fieldname: 'balance_to_pay',
                            fieldtype: 'Currency',
                            default: frm.doc.balance_amount,
                            read_only:1
                        },
                        {
                            label: '',
                            fieldname: 'column_break',
                            fieldtype: 'Column Break'
                        },
                        {
                            label: 'Payment Amount',
                            fieldname: 'amount_paid',
                            fieldtype: 'Currency',
                            default: frm.doc.balance_amount,
                            reqd:1
                        },
                        {
                            label: 'Mode of Payment',
                            fieldname: 'mode_of_payment',
                            fieldtype: 'Link',
                            options: 'Mode of Payment',
                            reqd:1
                        },
                        {
                            label: 'Transaction Reference #',
                            fieldname: 'transaction_reference',
                            fieldtype: 'Data'
                        }
                        ],
                    primary_action_label: ('Submit'),
                    primary_action: function() {
                        d.hide();
                        frm.save();
                        let row = frappe.model.add_child(frm.doc, 'Cart Payment', 'membership_payment'); 
                        frappe.model.set_value(row.doctype, row.name, 'mode_of_payment', d.get_value('mode_of_payment'));
                        frappe.model.set_value(row.doctype, row.name, 'paid_amount', d.get_value('amount_paid')); 
                    }
                });
                d.show();
            });
        }
        if (frm.doc.payment_status=="Paid" && !frm.doc.membership_document) {
            frm.add_custom_button(__('Create Membership'), function(){
                frappe.call({
                    method: 'club_crm.club_crm.doctype.memberships_application.memberships_application.create_membership',
                    args: {mem_application_id: frm.doc.name},
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
                frappe.msgprint({
                    title: __('Notification'),
                    indicator: 'green',
                    message: __('Membership Created successfully')
                });
                frm.save()
            });
        }
        if (frm.doc.membership_document) {
            frm.add_custom_button(__('View Membership'), function(){
                frappe.set_route("Form", "Memberships", frm.doc.membership_document);
            });
        }
    }
});

frappe.ui.form.on("Cart Payment", {
    membership_payment_remove: function(frm, cdt, cdn){
        var d = locals[cdt][cdn];
        var paid_amount = 0.0;
        frm.doc.membership_payment.forEach(function(d) { paid_amount += d.paid_amount; });
        frm.set_value('paid_amount', paid_amount);
        frm.save();
    }
});