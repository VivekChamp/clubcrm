frappe.views.calendar['Group Class'] = {
    field_map: {
        start: 'from_time',
        end: 'to_time',
        id: 'name',
        allDay: 'allDay',
        title: 'group_class_name',
        color: 'color'
    },
    gantt: false,
    options: {
        header: {
            left: 'prev, title, next',
            center: 'today'
        },
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',
        allDaySlot: false,
        editable: false
    },
    color_map: {
        "open": "purple",
        "scheduled": "green",
        "cancelled": "red",
        "completed": "blue"
    },
    get_css_class: function(data) {
        if (data.class_status == "Open") {
            return "open";
        } else if (data.class_status == "Scheduled") {
            return "scheduled";
        } else if (data.class_status == "Cancelled") {
            return "cancelled";
        } else if (data.class_status == "Completed") {
            return "completed";
        }
    }
};