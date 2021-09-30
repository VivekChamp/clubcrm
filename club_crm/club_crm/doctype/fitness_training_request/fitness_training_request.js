// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fitness Training Request", {
    refresh(frm) {
        //Hide Buttons on Child Table
        frm.fields_dict['customer_preference'].grid.wrapper.find('.grid-add-row').hide();
        frm.fields_dict['customer_preference'].grid.wrapper.find('.grid-remove-rows').hide();
    },
    request_status(frm) {
        if (frm.doc.request_status == "Scheduled") {
            frm.doc.scheduled_at = frappe.datetime.get_today();
            frm.refresh_field('scheduled_at');
        }
    }
});