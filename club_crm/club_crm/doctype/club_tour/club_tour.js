// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club Tour", "onload", function(frm) {
    frm.set_query("client_id", function() {
        return {
            "filters": [
                ["Client", "status", "not in", "Disabled"]
            ]
        }
    });
    frm.set_query("assign_cec", function() {
        return {
            "filters": [
                ["Service Staff", "cec_check", "=", "1"]
            ]
        }
    });
});

frappe.ui.form.on('Club Tour', {
    date: function(frm) {
        frm.set_value('from_time', '');
        frm.set_value('to_time', '');
    },
    validate: function(frm) {
            if (frm.doc.tour_status == "Scheduled") {
                if (!frm.doc.from_time || !frm.doc.to_time || !frm.doc.date) {
                    frappe.throw('Tour schedule is not set')
                }
            }
        }
        // from_time: function(frm) {
        //     if (!frm.doc.from_time) {
        //         frm.set_value('from_time', '');
        //     }
        // },
        // to_time: function(frm) {
        //     if (!frm.doc.to_time) {
        //         frm.set_value('to_time', '');
        //     }
        // }
});