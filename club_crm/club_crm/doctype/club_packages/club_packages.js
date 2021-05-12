// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club Packages", "onload", function(frm) {
    cur_frm.fields_dict.package_table.grid.get_field("service_type").get_query = function() {
        return {
            filters: [
                ["DocType", "name", "in", ["Spa Services", "Fitness Services", "Club Services"]]
            ]
        }
    }
});

frappe.ui.form.on('Club Package Item', {
    validity_in: function(frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        frappe.model.set_value(d.doctype, d.name, "validity_months", null);
        frappe.model.set_value(d.doctype, d.name, "validity", '0.0');
    }
});