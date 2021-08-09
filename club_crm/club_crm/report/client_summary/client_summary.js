// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Client Summary"] = {
    "filters": [{
            'fieldname': "membership_status",
            'label': "Membership Status",
            'fieldtype': "Select",
            'options': "\nMember\nNon-Member"
        },
        {
            'fieldname': "reg_on_app",
            'label': "Registered on app",
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
            "fieldname": "occupation_sector",
            "fieldtype": "Link",
            "label": "Occupation Sector",
            "options": "Industry Type"
        },
        {
            "fieldname": "vaccination_status",
            "fieldtype": "Select",
            "label": "Vaccination Status",
            "options": "\nVaccinated\nFirst shot\nNot vaccinated\nNo info"
        }
    ]
};