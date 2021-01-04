frappe.views.calendar['Spa Appointment'] = {
	field_map: {
		"start": "start",
		"end": "end",
		"id": "name",
		"title": "client_name",
		"allDay": "allDay",
		"eventColor": "color" 
	},
	order_by: "appointment_date",
	gantt: false,
	get_events_method: "club_crm.club_crm.doctype.spa_appointment.spa_appointment.get_events"
};

// frappe.views.calendar['Spa Appointment'] = {
//     field_map: {
//         start: 'start_time',
//         end: 'end_time',
//         id: 'name',
//         allDay: 'allDay',
//         title: 'client_name',
//         color: 'color'
//     }    
// }