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
});

// frappe.ui.form.on("Cart Appointment", "discount", function(frm, cdt, cdn) {
// 	var item = locals[cdt][cdn];
//     var total = unit_price * discount;
//     item.total_price = total;
// });

frappe.ui.form.on("Cart Appointment", {
	discount: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
        var net_total =0;
		var total_appointments = 0;
        var total_sessions = 0;
        var total_products = 0;
		frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price - (d.unit_price * d.discount/100));
        //frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price * d.discount/100);
        frm.doc.cart_appointment.forEach(function(d) { total_appointments += d.total_price; });
        frm.set_value('net_total_appointments', total_appointments);
        frm.set_value('net_total_sessions', total_sessions);
        frm.set_value('net_total_products', total_products);
        net_total = total_appointments + total_sessions + total_products;
        frm.set_value('net_total', net_total);
	},
    validate: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
        var net_total =0;
		var total_appointments = 0;
        var total_sessions = 0;
        var total_products = 0;
		frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price - (d.unit_price * d.discount/100));
        //frappe.model.set_value(d.doctype, d.name, "total_price", d.unit_price * d.discount/100);
        frm.doc.cart_appointment.forEach(function(d) { total_appointments += d.total_price; });
        frm.set_value('net_total_appointments', total_appointments);
        frm.set_value('net_total_sessions', total_sessions);
        frm.set_value('net_total_products', total_products);
        net_total = total_appointments + total_sessions + total_products;
        frm.set_value('net_total', net_total);
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