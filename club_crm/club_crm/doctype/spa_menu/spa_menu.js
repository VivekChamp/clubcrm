// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Spa Menu', {
	refresh: function(frm) {
	cur_frm.get_field('rooms').get_query = function(doc) {
        return {
            filters: [
                ["Club Room", "parent_club_room", "in", ["Male Room"]]
               ]
           };
       };
       cur_frm.get_field('female_room').get_query = function(doc) {
        return {
            filters: [
                ["Club Room", "parent_club_room", "in", ["Female Room"]]
               ]
           };
       };
	}
});