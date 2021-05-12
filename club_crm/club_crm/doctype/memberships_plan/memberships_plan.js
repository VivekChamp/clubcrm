// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Memberships Plan", "onload", function(frm) {
    frm.set_query("membership_type", function() {
        return {
            "filters": [
                ["Memberships Type", "enabled", "=", "1"]
            ]
        }
    });
    frm.set_query("membership_category", function() {
        return {
            "filters": [
                ["Memberships Category", "enabled", "=", "1"]
            ]
        }
    });
    frm.set_query("benefits_item", function() {
        return {
            "filters": [
                ["Club Packages", "package_type", "=", "Club"]
            ]
        }
    });
});

frappe.ui.form.on('Memberships Plan', {
    membership_duration: function(frm) {
        frm.set_value('duration_months', null);
        frm.set_value('duration', 0.0);
    }
});