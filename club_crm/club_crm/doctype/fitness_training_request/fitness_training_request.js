// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Fitness Training Request', {
// 	// refresh: function(frm) {

// 	// }
// });

frappe.ui.form.on("Fitness Training Request", {
    refresh(frm) {
        //Hide Buttons on Child Table
        frm.fields_dict['customer_preference'].grid.wrapper.find('.grid-add-row').hide();
        frm.fields_dict['customer_preference'].grid.wrapper.find('.grid-remove-rows').hide();
    }
});