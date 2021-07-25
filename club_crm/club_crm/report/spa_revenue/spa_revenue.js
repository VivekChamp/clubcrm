// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Spa Revenue"] = {
    "filters": [{
            "fieldname": "date_type",
            "label": __("Date Type"),
            "fieldtype": "Select",
            "default": "Booking Date",
            "options": "Booking Date\nAppointment Date"
        },
        {
            "fieldname": "gender",
            "fieldtype": "Link",
            "label": "Gender",
            "options": "Gender"
        },
        {
            'fieldname': "membership_status",
            'label': "Membership Status",
            'fieldtype': "Select",
            'options': "\nMember\nNon-Member"
        },
        {
            "fieldname": "spa_service",
            "fieldtype": "Link",
            "label": "Spa Service",
            "options": "Spa Services"
        },
        {
            "fieldname": "spa_category",
            "fieldtype": "Link",
            "label": "Spa Category",
            "options": "Spa Services Category"
        },
        {
            "fieldname": "service_staff",
            "fieldtype": "Link",
            "label": "Spa Therapist",
            "options": "Service Staff",
            "get_query": function() {
                return {
                    "filters": {
                        'spa_check': 1
                    }
                }
            }
        },
        {
            "fieldname": "club_room",
            "fieldtype": "Link",
            "label": "Room",
            "options": "Club Room"
        }
    ]
};