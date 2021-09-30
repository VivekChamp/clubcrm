// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Spa Commission Summary"] = {
    "filters": [{
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Link",
            options: "Fiscal Year",
            default: frappe.defaults.get_user_default("fiscal_year"),
            reqd: 1
        },
        {
            fieldname: "date_range",
            label: __("Range"),
            fieldtype: "Select",
            options: "Month\nCustom Range",
            default: "Month",
            reqd: 1
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
            default: "January",
            depends_on: "eval:doc.date_range=='Month'",
            mandatory_depends_on: "eval:doc.date_range=='Month'"
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            fieldtype: "Date",
            depends_on: "eval:doc.date_range=='Custom Range'",
            mandatory_depends_on: "eval:doc.date_range=='Custom Range'"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            depends_on: "eval:doc.date_range=='Custom Range'",
            mandatory_depends_on: "eval:doc.date_range=='Custom Range'"
        },
        {
            fieldname: "service_staff",
            label: __("Staff Name"),
            fieldtype: "Link",
            options: "Service Staff",
            filters: {
                "spa_check": 1
            }
        }
    ]
};