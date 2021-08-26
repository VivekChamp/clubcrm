// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Revenue"] = {
	"filters": [
		{
			fieldname: "cf_company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
			},
			{
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
			fieldname: "payment_type",
			label: __("Payment Type"),
			fieldtype: "Select",
			options: "\nOnline\nOffline"
			},
			{
			label: __("Application Type"),
			fieldname: "application_type",
			fieldtype: "Select",
			options:"\nSpa\nFitness\nClub\nRetail\nMembership\nFitness Training Request"
			},
			{
			fieldname: "membership_status",
			label: __("Membership Status"),
			fieldtype: "Select",
			options: "\nMember\nNon-Member"
			},
	]
};
