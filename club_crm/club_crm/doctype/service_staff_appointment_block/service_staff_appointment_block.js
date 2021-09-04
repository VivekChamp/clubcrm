// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Staff Appointment Block', {
    // refresh: function(frm) {

    // }
});

frappe.ui.form.on("Service Staff Appointment Block", {
    onload: function(frm) {
        // Filter service staff for spa appointment
        if (frm.doc.staff_category == "Spa") {
            frm.set_query("staff_name", function() {
                return {
                    "filters": {
                        'spa_check': 1
                    }
                }
            });
        }
    },
    staff_category: function(frm) {
        // Filter service staff for spa appointment
        if (frm.doc.staff_category == "Spa") {
            frm.set_query("staff_name", function() {
                return {
                    "filters": {
                        'spa_check': 1
                    }
                }
            });
        }
        if (frm.doc.staff_category == "Fitness") {
            frm.set_query("staff_name", function() {
                return {
                    "filters": {
                        'fitness_check': 1
                    }
                }
            });
        }
        if (frm.doc.staff_category == "CEC") {
            frm.set_query("staff_name", function() {
                return {
                    "filters": {
                        'cec_check': 1
                    }
                }
            });

        }
    }

});