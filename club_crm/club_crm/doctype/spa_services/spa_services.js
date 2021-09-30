// Copyright (c) 2021, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Spa Services', {
    refresh: function(frm) {
        frm.set_query("revenue_account", function() {
            return {
                "filters": [
                    ["Account", "root_type", "=", "Income"]
                ]
            }
        });
        //     cur_frm.get_field('male_rooms').get_query = function(doc) {
        //         return {
        //             filters: [
        //                 ["Club Room", "parent_club_room", "=", "Male Room"]
        //                 ["Club Room", "enabled", "=", "1"]
        //             ]
        //         };
        //     };
        //     cur_frm.get_field('female_rooms').get_query = function(doc) {
        //         return {
        //             filters: [
        //                 ["Club Room", "parent_club_room", "=", "Female Room"]
        //                 ["Club Room", "enabled", "=", "1"]
        //             ]
        //         };
        //     };
        // },

        // validate:function(frm) {
        //     if(!frm.doc.item){
        //      frappe.db.insert({
        //         "doctype" : "Item",
        //         "item_code": frm.doc.spa_name,
        //         "item_name": frm.doc.spa_name,
        //         "is_stock_item" : 0,
        //         "item_group": frm.doc.spa_category,
        //         "stock_uom": "Nos",
        //         "item_defaults.selling_cost_center": frm.doc.cost_center,
        //         "item_defaults.income_account" : frm.doc.revenue_account,
        //         "standard_rate": frm.doc.price
        //      }).then(c => {
        //             frappe.model.set_value(frm.doctype, frm.docname, 'Item', c);
        //             frm.set_value("item",c.name);
        //             frappe.show_alert({
        //                 message:__('Item is Created {0} Created', [c.name]),
        //                 indicator:'green'
        //             });
        //         });
        //     }
        //     if(frm.doc.item){
        //         frappe.call({
        //             "method": "frappe.client.set_value",
        //             "args":{
        //                 "doctype": "Item",
        //                 "name":frm.doc.item,
        //                 "fieldname":{
        //                     "item_code": frm.doc.spa_name,
        //                     "item_name":frm.doc.spa_name,
        //                     "item_group":frm.doc.spa_category,
        //                     "stock_uom":"Nos",
        //                     "item_defaults.selling_cost_center": frm.doc.cost_center,
        //                     "item_defaults.income_account" : frm.doc.revenue_account,
        //                     "standard_rate":frm.doc.price
        //                 }
        //             }
        //         })
        //     }
    }

});