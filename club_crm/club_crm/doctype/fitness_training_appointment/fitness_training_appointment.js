// For license information, please see license.txt

frappe.ui.form.on("Fitness Training Appointment", "onload", function(frm){
    frm.set_query("client_id", function(){
		return {
			"filters": [["Client", "status", "not in", "Disabled"]]
		}
	});
})
