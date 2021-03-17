// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client', {
	refresh(frm) {
		//Show alert pop-up everytime the client list is opened with the message from Alert section
		if (frm.doc.alerts && frm.doc.alert_type=="Everytime the client profile is opened"){
			frappe.msgprint({
				title: __('Staff Alerts'),
				indicator: 'red',
				message: __(frm.doc.alerts)
			});
		}

		//Create button with various functions	
		if (frm.doc.status!="Disabled") {
			frm.add_custom_button(__("Membership Application"), function() {
				var mem_app = frappe.model.get_new_doc("Memberships Application");
					mem_app.client=frm.doc.name;
					frappe.set_route('Form', 'Memberships Application', mem_app.name);
			},__("Create"));
		}

		//Display accounts receivable button	
		frm.add_custom_button(__('Accounts Receivable'), function() {
			frappe.set_route('query-report', 'Accounts Receivable', {customer:frm.doc.customer});
		});
		
		//Disable a client
		if (frm.doc.status!="Disabled") {
			frm.add_custom_button(__('Disable'), function() {
				frappe.confirm('Disable this client?',
					() => {
						// action to perform if Yes is selected
						frm.set_value('status', 'Disabled')
						frm.save()
    					.then(() => {
        				// do something after value is set
							frappe.msgprint({
								title: __('Notification'),
								indicator: 'red',
								message: __('This client has been disabled.')
							});
    					})
					}, () => {
						// action to perform if No is selected
					})
				// frappe.call({
				// 	method: 'club_crm.club_crm.doctype.client.client.disable_client',
				// 	args: {client_id: frm.doc.name},
				// 	callback: function(r) {
				// 		cur_frm.reload_doc();
				// 	}
				// });
				// frappe.msgprint({
				// 	title: __('Notification'),
				// 	indicator: 'red',
				// 	message: __('This client has been disabled.')
				// });
			});
		}

		//Enable a client
		if (frm.doc.status=="Disabled") {
			frm.add_custom_button(__('Enable'), function() {
				frappe.confirm('Disable this client?',
					() => {
						// action to perform if Yes is selected
						frm.set_value('status', 'Active')
						frm.save()
    					.then(() => {
        				// do something after value is set
							frappe.msgprint({
								title: __('Notification'),
								indicator: 'green',
								message: __('This client has been enabled.')
							});
    					})
					}, () => {
						// action to perform if No is selected
					})
				// frappe.call({
				// 	method: 'club_crm.club_crm.doctype.client.client.enable_client',
				// 	args: {client_id: frm.doc.name},
				// 	callback: function(r) {
				// 		cur_frm.reload_doc();
				// 	}
				// });
				// frappe.msgprint({
				// 	title: __('Notification'),
				// 	indicator: 'green',
				// 	message: __('This client has been enabled.')
				// });
			});
		}

		if (frm.doc.status=="Active") {
			frm.add_custom_button(__('Check-in'), function(){
				if (frm.doc.alerts && frm.doc.alert_type=="During client check-in only") {
					frappe.warn('Staff Alert', frm.doc.alerts,
						() => {
							// action to perform if continue is selected
							frappe.call({
								method: 'club_crm.club_crm.doctype.check_in.check_in.club_checkin',
								args: {client_id: frm.doc.name},
								callback: function(r) {
									cur_frm.reload_doc();
								}
							});
							frappe.msgprint({
								title: __('Notification'),
								indicator: 'green',
								message: __('Checked in successfully')
							});
						},
					'Continue Check-in', false)
				}
				else {
					frappe.call({
						method: 'club_crm.club_crm.doctype.check_in.check_in.club_checkin',
						args: {client_id: frm.doc.name},
						callback: function(r) {
							cur_frm.reload_doc();
						}
					});
					frappe.msgprint({
						title: __('Notification'),
						indicator: 'green',
						message: __('Checked in successfully')
					});
				}
			});
		}

		if (frm.doc.status=="Checked-in") {
		 	frm.add_custom_button(__('Check out'), function(){
				frappe.call({
					method: 'club_crm.club_crm.doctype.check_in.check_in.club_checkout',
					args: {client_id: frm.doc.name},
					callback: function(r) {
						cur_frm.reload_doc();
					}
				});
				frappe.msgprint({
					title: __('Notification'),
					indicator: 'green',
					message: __('Checked out successfully')
				});
		 	});
		}
	}
});

