// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

//Filtering of table columns based on conditions
frappe.ui.form.on("Cart", "onload", function(frm){
    frm.set_query("client_id", function(){
		return {
			"filters": [["Client", "status", "not in", "Disabled"]]
		}
	});
	frm.fields_dict.cart_appointment.grid.get_field("appointment_type").get_query = function(){
        return {
			filters: [["DocType", "name", "in", ["Spa Appointment", "Fitness Training Appointment"]]]
        }
	}
    frm.fields_dict.cart_appointment.grid.get_field("appointment_id").get_query = function(doc, cdt, cdn) {
        if(locals[cdt][cdn].appointment_type == "Spa Appointment"){
            return {
                filters: [["Spa Appointment", "payment_status", "=", "Not Paid"]]
            }
        }
        else if(locals[cdt][cdn].appointment_type == "Fitness Training Appointment"){
            return {
                filters: [["Fitness Training Appointment", "payment_status", "=", "Not Paid"]]
            }
        }
    }
    frm.fields_dict.cart_session.grid.get_field("package_name").get_query = function(doc, cdt, cdn){
        if(locals[cdt][cdn].package_type == "Spa"){
            return {
                filters: [["Club Packages", "package_type", "in", "Spa"]]
            }
        }
        if(locals[cdt][cdn].package_type == "Fitness"){
            return {
                filters: [["Club Packages", "package_type", "in", "Fitness"]]
            }
        }
	}
    frm.fields_dict.cart_product.grid.get_field("cart_item").get_query = function(){
        return {
			filters: [["Item", "item_group", "in", ["Body Care", "Facial Products", "Hair Care", "Skin Care", "Miscellaneous"]]]
        }
	}
    
});

frappe.ui.form.on("Cart", {
    refresh(frm) {
        //Hide Buttons on Child Table
        frm.fields_dict['payment_table'].grid.wrapper.find('.grid-add-row').hide();
        frm.fields_dict['cart_appointment'].grid.wrapper.find('.grid-add-row').hide();
        frm.fields_dict['cart_appointment'].grid.wrapper.find('.grid-remove-rows').hide();
		//Show payment button (with save the document)
        if(!frm.is_new() && !frm.is_dirty() && !frm.doc.balance_amount==0.0) {
            frm.add_custom_button(__('Offline Payment'), function() {
                if (frm.is_dirty()) {
                    frappe.msgprint({
                        title: __('Save Cart'),
                        indicator: 'red',
                        message: __('Please save the cart before making payment')
                    });
                }
                else {
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
                            let row = frappe.model.add_child(frm.doc, 'Cart Payment', 'payment_table'); 
                            frappe.model.set_value(row.doctype, row.name, 'mode_of_payment', d.get_value('mode_of_payment'));
                            frappe.model.set_value(row.doctype, row.name, 'paid_amount', d.get_value('amount_paid')); 
                        }
                    });
                    d.show();
                }
			});
        }
    },
    net_total_appointments: function(frm) {
        var net_total = 0.0;
        var grand_total = 0.0;
        net_total = frm.doc.net_total_appointments + frm.doc.net_total_sessions + frm.doc.net_total_products;
        frm.set_value('net_total', net_total);
        grand_total = frm.doc.net_total - frm.doc.discount_amount
        frm.set_value('grand_total', grand_total);
    },
    net_total_sessions: function(frm) {
        var net_total = 0.0;
        var grand_total = 0.0;
        net_total = frm.doc.net_total_appointments + frm.doc.net_total_sessions + frm.doc.net_total_products;
        frm.set_value('net_total', net_total);
        grand_total = frm.doc.net_total - frm.doc.discount_amount
        frm.set_value('grand_total', grand_total);
    },
    net_total_products: function(frm) {
        var net_total = 0.0;
        var grand_total = 0.0;
        net_total = frm.doc.net_total_appointments + frm.doc.net_total_sessions + frm.doc.net_total_products;
        frm.set_value('net_total', net_total);
        grand_total = frm.doc.net_total - frm.doc.discount_amount
        frm.set_value('grand_total', grand_total);
    },
    discount_amount: function(frm) {
        var grand_total = 0.0;
        grand_total = frm.doc.net_total - frm.doc.discount_amount
        frm.set_value('grand_total', grand_total);
    },
    apply_discount: function(frm) {
        var discount_amount = 0.0;
        var discount_percentage = 0.0;
        frm.set_value('discount_amount', discount_amount);
        frm.set_value('discount_percentage', discount_percentage );
    },
    discount_percentage: function(frm){
        var discount = 0.0;
        discount = frm.doc.net_total * frm.doc.discount_percentage/100;
        frm.set_value('discount_amount', discount);
    },
    grand_total:function(frm){
        frm.set_value('total_to_be_paid', frm.doc.grand_total);
    },
    total_to_be_paid:function(frm){
        frm.set_value('balance_amount', frm.doc.total_to_be_paid - frm.doc.paid_amount); 
    }
    // paid_amount:function(frm){
    //     frm.set_value('balance_amount', frm.doc.total_to_be_paid - frm.doc.paid_amount);
    // },
    // balance_amount:function(frm) {
    //     if (frm.doc.balance_amount==0) {
    //         frm.set_value('payment_status', 'Paid');
    //         frm.refresh();
    //     }
    // }
});

frappe.ui.form.on("Cart Appointment", {
    unit_price: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var total_appointments = 0.0;
		frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price - (d.unit_price * d.discount/100));
        frm.doc.cart_appointment.forEach(function(d) { total_appointments += d.total_price; });
        frm.set_value('net_total_appointments', total_appointments);
	},
	discount: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var total_appointments = 0.0;
		frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price - (d.unit_price * d.discount/100));
        frm.doc.cart_appointment.forEach(function(d) { total_appointments += d.total_price; });
        frm.set_value('net_total_appointments', total_appointments);
	}
});

frappe.ui.form.on("Cart Product", {
    unit_price: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_products = 0.0;
		frappe.model.set_value(d.doctype, d.name, "total_price", (d.unit_price * d.qty) - ((d.unit_price * d.qty) * d.discount/100));
        frm.doc.cart_product.forEach(function(d) { total_products += d.total_price; });
        frm.set_value('net_total_products', total_products);
    },
	qty: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
        var total_products = 0.0;
		frappe.model.set_value(d.doctype, d.name, "total_price", (d.unit_price * d.qty) - ((d.unit_price * d.qty) * d.discount/100));
        frm.doc.cart_product.forEach(function(d) { total_products += d.total_price; });
        frm.set_value('net_total_products', total_products);
	},
    discount: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_products = 0.0;
		frappe.model.set_value(d.doctype, d.name, "total_price", (d.unit_price * d.qty) - ((d.unit_price * d.qty) * d.discount/100));
        frm.doc.cart_product.forEach(function(d) { total_products += d.total_price; });
        frm.set_value('net_total_products', total_products);
    },
    cart_product_remove: function(frm){
        frm.save();
    }
});

frappe.ui.form.on('Cart Product', 'cart_item', function(frm, cdt, cdn){
    var d = locals[cdt][cdn];
    frappe.model.set_value(d.doctype, d.name, "qty", "1");
    frappe.model.set_value(d.doctype, d.name, "discount", "0");
});

frappe.ui.form.on("Cart Session", {
    unit_price: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_sessions = 0.0;
        frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price - (d.unit_price * d.discount/100));
        frm.doc.cart_session.forEach(function(d) { total_sessions += d.total_price; });
        frm.set_value('net_total_sessions', total_sessions);
    },
    discount: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        var total_sessions = 0.0;
        frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price - (d.unit_price * d.discount/100));
        frm.doc.cart_session.forEach(function(d) { total_sessions += d.total_price; });
        frm.set_value('net_total_sessions', total_sessions);
    },
    cart_session_remove: function(frm){
        frm.save();
    }
});

frappe.ui.form.on('Cart Session', 'package_type', function(frm, cdt, cdn){
    var d = locals[cdt][cdn];
    frappe.model.set_value(d.doctype, d.name, "package_name", "");
    frappe.model.set_value(d.doctype, d.name, "unit_price", "");
    frappe.model.set_value(d.doctype, d.name, "discount", "");
});

frappe.ui.form.on("Cart Payment", {
    payment_table_remove: function(frm, cdt, cdn){
        var d = locals[cdt][cdn];
        var paid_amount = 0.0;
        frm.doc.payment_table.forEach(function(d) { paid_amount += d.paid_amount; });
        frm.set_value('paid_amount', paid_amount);
        frm.save();
    }
});

frappe.ui.form.on('Cart Appointment', 'appointment_id', function(frm, cdt, cdn){
    if(locals[cdt][cdn].appointment_type == "Spa Appointment"){
        frappe.call({
            'method': 'frappe.client.get_value',
            'args': {
                'doctype': 'Spa Appointment',
                'filters': [
                    ['Spa Appointment', 'name', '=', locals[cdt][cdn].appointment_id]
                ],
            'fieldname': ['spa_service', 'default_price']
            },
            'callback': function(r){
                frappe.model.set_value(cdt, cdn, 'description', r.message.spa_service);
                frappe.model.set_value(cdt, cdn, 'unit_price', r.message.default_price);
            }
        });
    }
    else if(locals[cdt][cdn].appointment_type == "Fitness Training Appointment"){
        frappe.call({
            'method': 'frappe.client.get_value',
            'args': {
                'doctype': 'Fitness Training Appointment',
                'filters': [
                    ['Fitness Training Appointment', 'name', '=', locals[cdt][cdn].appointment_id]
                ],
            'fieldname': ['fitness_service', 'default_price']
            },
            'callback': function(r){
                frappe.model.set_value(cdt, cdn, 'description', r.message.fitness_service);
                frappe.model.set_value(cdt, cdn, 'unit_price', r.message.default_price);
            }
        });
    }
});
