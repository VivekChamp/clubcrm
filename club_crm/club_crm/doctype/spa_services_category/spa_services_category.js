// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Spa Services Category', {
	validate:function(frm){
	    if(!frm.doc.item_category){
	     frappe.db.insert({
	         "doctype" :"Item Group",
	             "item_group_name":frm.doc.spa_category_name,
	             "parent_item_group":'Treatments'
	     }).then(c => {
                frappe.model.set_value(frm.doctype, frm.docname, 'Item Group', c);
                frm.set_value("item_category",c.name);
            });
	    }
	}
});