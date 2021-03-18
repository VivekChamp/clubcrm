// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cart", "onload", function(frm){
	cur_frm.fields_dict.cart_appointment.grid.get_field("appointment_type").get_query = function(){
        return {
			filters: [
                ["DocType", "name", "in", ["Spa Appointment", "Fitness Training Appointment"]]
            ]
        }
	}
    cur_frm.fields_dict.cart_appointment.grid.get_field("appointment_id").get_query = function(doc, cdt, cdn) {
        if(locals[cdt][cdn].appointment_type == "Spa Appointment"){
            return {
                filters: [
                    ["Spa Appointment", "payment_status", "=", "Not Paid"]
                ]
            }
        }
        else if(locals[cdt][cdn].appointment_type == "Fitness Training Appointment"){
            return {
                filters: [
                    ["Fitness Training Appointment", "payment_status", "=", "Not Paid"]
                ]
            }
        }
    }
    cur_frm.fields_dict.cart_product.grid.get_field("cart_item").get_query = function(){
        return {
			filters: [
                ["Item", "item_group", "in", ["Body Care", "Facial Products", "Hair Care", "Skin Care", "Miscellaneous"]]
            ]
        }
	}
});

frappe.ui.form.on("Cart", {
    refresh(frm) {
		//Show payment button
        if(!frm.is_new() && !frm.is_dirty()) {
            frm.add_custom_button(__('Offline Payment'), function() {
                if (frm.is_dirty()) {
                    frappe.msgprint({
                        title: __('Save Cart'),
                        indicator: 'red',
                        message: __('Please save the cart before making payment')
                    });
                }
                else{

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
        //if (frm.doc.apply_discount=="None") {
            frm.set_value('discount_amount', discount_amount);
            frm.set_value('discount_percentage', discount_percentage );
        //}
        // else if (frm.doc.apply_discount=="Percentage on Net Total") {
        //     discount = frm.doc.net_total * frm.doc.discount_percentage/100;
        //     frm.set_value('discount_amount', discount);
        // }
    },
    discount_percentage: function(frm){
        var discount = 0.0;
        discount = frm.doc.net_total * frm.doc.discount_percentage/100;
        frm.set_value('discount_amount', discount);
    }
});

frappe.ui.form.on("Cart Appointment", {
	discount: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
        var net_total = 0.0;
		var total_appointments = 0.0;
		frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price - (d.unit_price * d.discount/100));
        frm.doc.cart_appointment.forEach(function(d) { total_appointments += d.total_price; });
        frm.set_value('net_total_appointments', total_appointments);
	}
});

frappe.ui.form.on("Cart Product", {
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