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
                titleFormat: 'ddd, DD MMMM YYYY',
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
                titleFormat: 'ddd, DD MMMM YYYY',
                duration: { days: 1 },
                buttonText: 'Day',
                slotDuration: "01:00",
                slotLabelInterval: "01:00",
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
        "paid_scheduled": "green",
        "paid_open": "purple",
        "paid_check": "dark-green",
        "paid_complete": "blue",
        "noshow_cancel": "gray",
        "unpaid_scheduled": "red",
        "unpaid_open_draft": "pink",
        "unpaid_check": "orange",
        "unpaid_complete": "yellow",
        "background": "#b9fff5"
    },
    get_events_method: "club_crm.club_crm.doctype.spa_appointment.spa_appointment.get_events",
    get_css_class: function(data) {
        if (data.rendering == "background") {
            return "background";
        }
        if (data.payment_status == "Paid" && data.appointment_status == "Scheduled") {
            return "paid_scheduled";
        } else if (data.payment_status == "Paid" && data.appointment_status == "Open") {
            return "paid_open";
        } else if (data.payment_status == "Paid" && data.appointment_status == "Checked-in") {
            return "paid_check";
        } else if (data.payment_status == "Paid" && data.appointment_status == "Complete") {
            return "paid_complete";
        } else if (data.appointment_status == "No Show" || data.appointment_status == "Cancelled") {
            return "noshow_cancel";
        } else if ((data.payment_status == "Not Paid" || data.payment_status == "Added to cart") && data.appointment_status == "Scheduled") {
            return "unpaid_scheduled";
        } else if ((data.payment_status == "Not Paid" || data.payment_status == "Added to cart") && data.appointment_status == "Open") {
            return "unpaid_open_draft";
        } else if ((data.payment_status == "Not Paid" || data.payment_status == "Added to cart") && data.appointment_status == "Checked-in") {
            return "unpaid_check";
        } else if ((data.payment_status == "Not Paid" || data.payment_status == "Added to cart") && data.appointment_status == "Complete") {
            return "unpaid_complete";
        } else if ((data.payment_status == "Not Paid" || data.payment_status == "Added to cart") && data.appointment_status == "Draft") {
            return "unpaid_open_draft";
        }
    }
};