// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

//Filtering of table columns based on conditions
frappe.ui.form.on("Additional Benefits", "onload", function(frm) {
    frm.set_query("client_id", function() {
        return {
            "filters": [
                ["Client", "status", "not in", "Disabled"],
                ["Client", "membership_status", "=", "Member"]
            ]
        }
    })
    frm.set_query("membership", function() {
        return {
            "filters": [
                ["Memberships", "membership_status", "in", ["Active", "Draft"]]
            ]
        }
    })
    cur_frm.fields_dict.additional_benefits_item.grid.get_field("service_type").get_query = function() {
        return {
            filters: [
                ["DocType", "name", "in", ["Spa Services", "Fitness Services", "Club Services"]]
            ]
        }
    }
    cur_frm.fields_dict.additional_benefits_item.grid.get_field("service_name").get_query = function() {
        return {
            filters: [
                ["session_type", "=", "Complimentary"]
            ]
        }
    }
});

frappe.ui.form.on('Additional Benefits Item', 'service_type', function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    frappe.model.set_value(d.doctype, d.name, "service_name", "");
});

frappe.ui.form.on("Additional Benefits", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus == 1 && frm.doc.workflow_state == "Approved" && frm.doc.benefit_activated == 0) {
            frm.add_custom_button(__('Activate'), function() {
                frappe.call({
                    method: 'club_crm.club_crm.doctype.additional_benefits.additional_benefits.activate_additional_benefits',
                    args: { doc_id: frm.doc.name },
                    callback: function(r) {
                        cur_frm.reload_doc();
                    }
                });
            });


        }
    }
});