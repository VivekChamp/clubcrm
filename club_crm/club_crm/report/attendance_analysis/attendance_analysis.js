// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Analysis"] = {
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
            fieldname: "report_type",
            label: __("Report Type"),
            fieldtype: "Select",
            options: "\nBy Packages\nBy Services",
            reqd: 1
        },
        {
            label: __("Package Type"),
            fieldname: "package_type",
            fieldtype: "Select",
            options: "All Packages\nSpa\nFitness",
            depends_on: "eval:doc.report_type=='By Packages'",
            default: "All Packages"
        },
        {
            label: __("Service Type"),
            fieldname: "service_type",
            fieldtype: "Select",
            options: "Fitness\nSpa",
            depends_on: "eval:doc.report_type=='By Services'",
            default: "Fitness"
        },
        {
            fieldname: "service_staff",
            label: __("Service Staff"),
            fieldtype: "Link",
            options: "Service Staff",
            default: "None"
        }
    ]
};