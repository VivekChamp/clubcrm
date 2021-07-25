// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Club Sales Summary"] = {
    "filters": [{
            fieldname: "from_date",
            label: __("From Date"),
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
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
            label: __("Sales Type"),
            fieldname: "type",
            fieldtype: "Select",
            options: "\nSpa\nRetail\nFitness\nMembership\nOthers"
        },
        {
            fieldname: "membership_status",
            label: __("Membership Status"),
            fieldtype: "Select",
            options: "\nMember\nNon-Member"
        },
        {
            fieldname: "transaction_type",
            label: __("Transaction Type"),
            fieldtype: "Select",
            options: "\nOnline\nOffline"
        },
    ]
};