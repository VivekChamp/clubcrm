// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Service Staff Availability", {
    refresh(frm) {
        //Hide Buttons on Child Table
        frm.fields_dict['week_1'].grid.wrapper.find('.grid-add-row').hide();
		frm.fields_dict['week_2'].grid.wrapper.find('.grid-add-row').hide();
		frm.fields_dict['week_3'].grid.wrapper.find('.grid-add-row').hide();
		frm.fields_dict['week_4'].grid.wrapper.find('.grid-add-row').hide();
		frm.fields_dict['week_5'].grid.wrapper.find('.grid-add-row').hide();
		frm.fields_dict['week_6'].grid.wrapper.find('.grid-add-row').hide();
	},
	month(frm) {
		if (frm.doc.staff_name) {
			frm.save();
		}
	},
	staff_name(frm) {
		if (frm.doc.month) {
			frm.save();
		}
	}
});