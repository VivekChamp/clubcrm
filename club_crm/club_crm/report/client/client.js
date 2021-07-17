// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Client"] = {
    "filters": [{
            'fieldname': "membership_status",
            'label': "Membership Status",
            'fieldtype': "Select",
            'options': "\nMember\nNon-Member"
        },
        {
            'fieldname': "reg_on_app",
            'label': "App Users",
            'fieldtype': "Select",
            'options': "\nYes\nNo"
        },
        {
            "fieldname": "gender",
            "fieldtype": "Link",
            "label": "Gender",
            "options": "Gender"
        },
        {
            "fieldname": "nationality",
            "fieldtype": "Link",
            "label": "Nationality",
            "options": "Country"
        },
        {
            "fieldname": "assigned_to",
            "fieldtype": "Link",
            "label": "Assigned to",
            "options": "Service Staff",
            "get_query": function() {
                return {
                    "filters": {
                        'cec_check': 1
                    }
                }
            }
        },
        {
            "fieldname": "vaccination_status",
            "fieldtype": "Select",
            "label": "Vaccination Status",
            "options": "\nVaccinated\nFirst shot\nNot vaccinated\nNo info"
        },
        {
            'fieldname': "membership_plan",
            'label': "Membership Plan",
            'fieldtype': "Link",
            'options': "Memberships Plan",
            'depends_on': "eval: doc.membership_status == 'Member'"
        }
    ]
};