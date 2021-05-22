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
    },
    gantt: false,
    options: {
        header: {
            left: 'prev, title, next',
            center: 'today',
            right: ' listOneWeek, listOneDay, agendaOneDay, agendaOneWeek, timelineOneDay'
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
                buttonText: 'Day',
                slotDuration: "00:30:00",
                minTime: "08:00:00",
                maxTime: "22:00:00"
            },
            agendaOneWeek: {
                type: 'agendaDay',
                duration: { days: 7 },
                buttonText: 'Week',
                slotDuration: "01:00:00",
                minTime: "08:00:00",
                maxTime: "22:00:00"
            },
            timelineOneDay: {
                type: 'timeline',
                duration: { days: 1 },
                buttonText: 'Timeline',
                minTime: "08:00:00",
                maxTime: "22:00:00"
            }
        },
        resources: function(callback) {
            return frappe.call({
                method: "club_crm.club_crm.doctype.spa_appointment.spa_appointment.get_therapist_resources",
                type: "GET",
                callback: function(r) {
                    var resources = r.message || [];
                    callback(resources);
                }
            })
        },
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        defaultView: 'agendaOneDay',
        allDaySlot: false,
        slotEventOverlap: false,
        editable: false
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
    color_map: {
        "paid": "blue",
        "open": "purple",
        "scheduled": "green",
        "checked-in": "yellow",
        "no-show": "red",
        "draft": "pink",
        "completed": "blue",
        "background": "#b9fff5"
    },
    get_events_method: "club_crm.club_crm.doctype.spa_appointment.spa_appointment.get_events",
    get_css_class: function(data) {
        if (data.rendering == "background") {
            return "background";
        }
        if (data.payment_status == "Paid") {
            return "paid";
        } else if (data.appointment_status == "Open") {
            return "open";
        } else if (data.appointment_status == "Scheduled") {
            return "scheduled";
        } else if (data.appointment_status == "Checked-in") {
            return "checked-in";
        } else if (data.appointment_status == "No Show") {
            return "no-show";
        } else if (data.appointment_status == "Draft") {
            return "draft";
        } else if (data.appointment_status == "Completed") {
            return "completed";
        }
    }
};