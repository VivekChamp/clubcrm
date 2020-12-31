// Copyright (c) 2020, Blue Lynx and contributors
// For license information, please see license.txt

frappe.ui.form.on('Spa Appointment', {
	// refresh: function(frm) {

	// }
	onload: function(frm) {
		if (frm.is_new()) {
			frm.set_value('appointment_time', null);
			frm.disable_save();
		}
	},

	refresh: function(frm) {
		if (frm.is_new()) {
			frm.page.set_primary_action(__('Check Availability'), function() {
				if (!frm.doc.client_id) {
					frappe.msgprint({
						title: __('Not Allowed'),
						message: __('Please select Client ID first'),
						indicator: 'red'
					});
				} else if (!frm.doc.spa_item) {
					frappe.msgprint({
						title: __('Not Allowed'),
						message: __('Please select Spa Treatment'),
						indicator: 'red'
					});
				} else {
					check_and_set_availability(frm);
				}
			});
		} else {
			frm.page.set_primary_action(__('Update'), () => frm.save('Update'));
		}

		if(frm.doc.docstatus==1 && frm.doc.payment_status == "Not Paid"){
			frm.add_custom_button(__('Offline Payment'), function() {
				  
						  let d = new frappe.ui.Dialog({
						  title: 'Offline Payment',
						  fields: [
						  {
							  label: 'Transaction Date',
							  fieldname: 'transaction_date',
							  fieldtype: 'Date',
							  default:'Today',
							  read_only:1
						  },
						  {
							  label: 'Paid Amount',
							  fieldname: 'amount',
							  fieldtype: 'Currency',
							  reqd:1
						  },
						  {
							  label: '',
							  fieldname: 'column_break',
							  fieldtype: 'Column Break'
						  },
						  {
							  label: 'Payment Method',
							  fieldname: 'payment_type',
							  fieldtype: 'Select',
							  options:['Credit Card','Cash'],
							  reqd:1
						  },
						  {
							  label: 'Transaction Reference #',
							  fieldname: 'transaction_reference',
							  fieldtype: 'Data',
							  depends_on: 'eval:doc.payment_type=="Credit Card"'
						  }
					  ],
				   primary_action_label: ('Submit'),
					 primary_action: function() {
					  d.hide();
					  frm.enable_save();
					  frm.save('Update');
						frm.set_value("paid_amount",d.get_value('amount'));
						frm.set_value("payment_method",d.get_value('payment_type'));
						frm.set_value("transaction_date",d.get_value('transaction_date'));
						frm.set_value("transaction_reference",d.get_value('transaction_reference'));
						frm.set_value("payment_status","Paid");
						frm.set_value("status","Scheduled");
					 }
					});
					d.show();
				  });
				  }
	
	}
	
	// refresh: function(frm) {
	// 		
	// }
});

let check_and_set_availability = function(frm) {
	let selected_slot = null;

	show_availability();

	function show_empty_state(spa_therapist, appointment_date) {
		frappe.msgprint({
			title: __('Not Available'),
			message: __('Spa Therapist {0} not available on {1}', [spa_therapist.bold(), appointment_date.bold()]),
			indicator: 'red'
		});
	}

	function show_availability() {
		let selected_therapist = '';
		let d = new frappe.ui.Dialog({
			title: __('Available slots'),
			fields: [
				{ fieldtype: 'Link', options: 'Spa Menu', reqd: 1, fieldname: 'spa_item', label: 'Spa Menu'},
				{ fieldtype: 'Column Break'},
				{ fieldtype: 'Link', options: 'Spa Therapist', reqd: 1, fieldname: 'spa_therapist', label: 'Spa Therapist'},
				{ fieldtype: 'Column Break'},
				{ fieldtype: 'Date', reqd: 1, fieldname: 'appointment_date', label: 'Date'},
				{ fieldtype: 'Section Break'},
				{ fieldtype: 'HTML', fieldname: 'slots'}

			],
			primary_action_label: __('Book'),
			primary_action: function() {
				frm.set_value('appointment_time', selected_slot);
				frm.set_value('spa_therapist', d.get_value('spa_therapist'));
				frm.set_value('spa_item', d.get_value('spa_item'));
				frm.set_value('appointment_date', d.get_value('appointment_date'));
				d.hide();
				frm.enable_save();
				frm.save('Submit');
				d.get_primary_btn().attr('disabled', true);
			}
		});

		d.set_values({
			'spa_item': frm.doc.spa_item,
			'spa_therapist': frm.doc.spa_therapist,
			'appointment_date': frm.doc.appointment_date
		});

		// disable dialog action initially
		d.get_primary_btn().attr('disabled', true);

		// Field Change Handler

		let fd = d.fields_dict;

		d.fields_dict['appointment_date'].df.onchange = () => {
			show_slots(d, fd);
		};
		d.fields_dict['spa_therapist'].df.onchange = () => {
			if (d.get_value('spa_therapist') && d.get_value('spa_therapist') != selected_therapist) {
				selected_therapist = d.get_value('spa_therapist');
				show_slots(d, fd);
			}
		};
		d.show();
	}

	function show_slots(d, fd) {
		if (d.get_value('appointment_date') && d.get_value('spa_therapist')) {
			fd.slots.html('');
			frappe.call({
				method: 'club_crm.api.spa.get_slots',
				args: {
					therapist_name: d.get_value('spa_therapist'),
					date: d.get_value('appointment_date'),
					spa_item: d.get_value('spa_item')
				},
				callback: (r) => {
					let data = r.message;
					if (data.available_slots.length > 0) {
						let $wrapper = d.fields_dict.slots.$wrapper;

						// make buttons for each slot
						let available_slots = data.available_slots;
						let slot_html = '';
						let i=0;
						slot_html = slot_html + `<label>Select a time slot</label>`;
						slot_html = slot_html + `<br/>` +`<br/>` + available_slots.map(slot => {
							let start_str= slot;
							return `<button class="btn btn-default"
						 			data-name=${start_str}
						 			style="margin: 0 10px 10px 0; width: 72px;">
						 			${start_str.substring(0, start_str.length - 3)}
						 		</button>`;
							
						}).join("");
						slot_html = slot_html + `<br/>`;

						$wrapper
							.css('margin-bottom', 0)
							.addClass('text-center')
							.html(slot_html);

						// blue button when clicked
						$wrapper.on('click', 'button', function() {
							let $btn = $(this);
							$wrapper.find('button').removeClass('btn-primary');
							$btn.addClass('btn-primary');
							selected_slot = $btn.attr('data-name');
							// duration = $btn.attr('data-duration');
							// enable dialog action
							d.get_primary_btn().attr('disabled', null);
						});

					} else {
						//	fd.available_slots.html('Please select a valid date.'.bold())
						show_empty_state(d.get_value('spa_therapist'), d.get_value('appointment_date'));
					}
				},
				freeze: true,
				freeze_message: __('Fetching records......')
			});
		} else {
			fd.available_slots.html(__('Appointment date and therapist name are mandatory').bold());
		}
	}
};