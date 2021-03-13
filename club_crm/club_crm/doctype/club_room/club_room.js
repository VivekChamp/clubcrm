// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on("Club Room", "onload", function(frm){
    cur_frm.set_query("club_room_type", function(){
        return {
            "filters": [
                ["Club Room Type", "enabled", "=", "1"]
            ]
        }
    });
})
