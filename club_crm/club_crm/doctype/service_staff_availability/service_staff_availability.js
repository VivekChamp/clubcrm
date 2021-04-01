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

});

// frappe.ui.form.on("Service Staff Availability", "refresh", function(frm){
// 	var idx = 1;
// 	frm.doc.week_1.sort(function(a,b){
//   		if (a.date < b.date){ return -1 }
//  	 	else if ( a.date > b.date){ return 1 }
//  	 	return 1;
// 	});

// 	frm.doc.week_1.map(function(item){
//   		item.idx = idx++;
// 	});
// });
