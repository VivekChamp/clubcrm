// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

// \nBy Category\nBy Transaction Type

frappe.query_reports["Daily Closeout"] = {
    "filters": [{
            fieldname: "from_date",
            label: __("From Date"),
            default: frappe.datetime.get_today(),
            fieldtype: "Date",
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            label: __("Report Type"),
            fieldname: "report_type",
            fieldtype: "Select",
            options: "\nBy Payment Type\nBy Category\nBy Transaction Type",
            reqd: 1
        }
    ]
};