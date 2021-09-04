// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Club Services', {
    refresh: function(frm) {
        frm.set_query("revenue_account", function() {
            return {
                "filters": [
                    ["Account", "root_type", "=", "Income"]
                ]
            }
        });
    }
});