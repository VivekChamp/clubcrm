// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Extend Validity', {
    onload: function(frm) {
        frm.disable_save();
    },
    extend_on: function(frm) {
        frm.set_value('membership_category', null);
        frm.set_value('session_service_type', null);
    }
});