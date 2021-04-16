frappe.views.calendar["Spa Appointment"] = {
	field_map: {
		"start": "start_time",
		"end": "end_time",
		"title": "title",
		"allDay": "allDay",
		"description": "notes",
		"resourceId": "service_staff",
		"color": "color",
		"rendering": "rendering"
		// "description": "description",
        // "name": "name",
		
	},
	//order_by: "appointment_date",
	gantt: true,
	options: {
		        header: {
		            left: 'title',
		            center: 'prev,today,next',
		            right: 'listOneWeek,listOneDay agendaOneDay,agendaOneWeek timelineOneDay'
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
					  slotDuration: "01:00:00",
					  minTime: "08:00:00",
					  maxTime: "22:00:00"
					},
					agendaOneWeek: {
						type: 'agendaDay',
						duration: { days: 7 },
						buttonText: 'Week Overview',
						slotDuration: "01:00:00",
						minTime: "08:00:00",
						maxTime: "22:00:00"
					},
					timelineOneDay: {
						type: 'timeline',
						duration: { days: 1 },
						buttonText: 'Day Timeline',
						minTime: "08:00:00",
						maxTime: "22:00:00"
					  }
				},
				resources: function(callback) {
					return frappe.call({
						method:"club_crm.club_crm.doctype.spa_appointment.spa_appointment.get_therapist_resources",
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
				eventTextColor : '#ffffff',
				// eventRender: function(eventObj, $el) {
				// 	$el.popover({
				// 	  title: "Notes",
				// 	  html: true,
				// 	  content: eventObj.description,
				// 	  trigger: 'hover',
				// 	  placement: 'top',
				// 	  container: 'body'
				// 	});
				//   },
		    },
	get_events_method: "club_crm.club_crm.doctype.spa_appointment.spa_appointment.get_events"
};