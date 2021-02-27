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
	options: {
		header: {
			        left: 'title',
			        center: '',
			        right: 'prev,today,next month,agendaWeek,agendaDay listTenDays,listOneDay,timelineOneDay'
			    },
		views: {
					listOneDay: {
						type: 'list',
						duration: { days: 1 },
						buttonText: '1 day list'
					},
					listTenDays: {
						type: 'list',
						duration: { days: 10 },
						buttonText: '10 day list'
					},
					timelineOneDay: {
						type: 'agendaDay',
						duration: { days: 1 },
						buttonText: 'Resource List'
					}
				},
		groupByDateAndResource: true,
		resources: [
						{ id: 'a', title: 'Res A' },
						{ id: 'b', title: 'Res B' },
					],
		defaultView: 'timelineOneDay'
		},
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

// frappe.views.calendar['Spa Appointment'] = {
// 	field_map: {
// 		"start": "start_time",
// 		"end": "end_time",
// 		"id": "name",
// 		"title": "client_name",
// 		"allDay": "allDay",
//         "color": "status",
//         // "doctype": "Spa Appointment",
// 		// "description": "description",
//         // "name": "name",
// 		// "rendering": "rendering",
// 		// 'resourceId': "spa_therapist"

// 	},
// 	schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',

// 	options: {
//         header: {
//             left: 'title',
//             center: '',
//             right: 'prev,today,next month,agendaWeek,agendaDay listTenDays,listOneDay,timelineOneDay'
//         },
// 		views: {
// 			listOneDay: {
// 			  type: 'list',
// 			  duration: { days: 1 },
// 			  buttonText: '1 day list'
// 			},
// 			listTenDays: {
// 			  type: 'list',
// 			  duration: { days: 10 },
// 			  buttonText: '10 day list'
// 			},
// 			// agendaOneDay: {
// 			//   type: 'agenda',
// 			//   duration: { days: 1 },
// 			//   buttonText: 'Agenda Day'
// 			// },
// 			timelineOneDay: {
// 			  type: 'agendaDay',
// 			  duration: { days: 1 },
// 			  buttonText: 'Resource List'
// 			}
// 		  },

		
// 		//groupByDateAndResource: "True",
// 		groupByResource: true,
// 		//firstDay: 1,
// 		//resourceGroupField: 'spa_therapist',
// 		resources: [
// 			{ id: 'a', title: 'Res A' },
// 			{ id: 'b', title: 'Res B' },
// 		  ],
// 		events: [

// 		],
// 		//slotDuration: "00:15:00",
// 		defaultView: 'timelineOneDay'
// 		//resourceLabelText: 'Therapist',
        
//     }
//     //this method will return list also with resource id
// 	//get_events_method: "my_custom_method",

// }