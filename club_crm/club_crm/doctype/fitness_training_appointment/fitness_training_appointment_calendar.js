
frappe.views.calendar["Fitness Training Appointment"] = {
	field_map: {
		"start": "start_time",
		"end": "end_time",
		"title": "title",
		"allDay": "allDay",
		"description": "notes",
		"resourceId": "fitness_trainer",
		"color": "color",
		"eventTextColor": "textcolor"
	},
	gantt: true,
	options: {
		        header: {
		            left: 'title',
		            center: 'prev,today,next',
		            right: 'listOneWeek,listOneDay agendaOneDay'
		        },
				views: {
					listOneDay: {
					  type: 'list',
					  duration: { days: 1 },
					  buttonText: 'Day list',
					  noEventsMessage: "No appointments for this date"
					},
					listOneWeek: {
					  type: 'list',
					  duration: { days: 7 },
					  buttonText: 'Week list',
					  noEventsMessage: "No appointments for this week"
					},
					agendaOneDay: {
					  type: 'agendaDay',
					  duration: { days: 1 },
					  buttonText: 'Day Overview',
					  minTime: "08:00:00",
					  maxTime: "22:00:00"
					}
				},
				resources: function(callback) {
					return frappe.call({
						method:"club_crm.club_crm.doctype.fitness_training_appointment.fitness_training_appointment.get_trainer_resources",
						type: "GET",
						callback: function(r) {
							 var resources = r.message || [];
							 callback(resources);
							}
					})
				},
				schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
				defaultView: 'agendaOneDay',
				allDaySlot:false,
				slotEventOverlap:false,
				eventTextColor : '#ffffff'
		    },
	get_events_method: "club_crm.club_crm.doctype.spa_appointment.spa_appointment.get_events"
};