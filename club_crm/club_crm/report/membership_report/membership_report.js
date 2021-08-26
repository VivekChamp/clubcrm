// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Membership Report"] = {
	"filters": [
		{
            "fieldname": "membership_category",
            "fieldtype": "Link",
            "label": "Membership Category",
            "options": "Memberships Category"
        },
		{
            "fieldname": "memberships_type",
            "fieldtype": "Select",
            "label": "Membership Type",
            "options": "\nNew\nEarly Renew\nLate Renew"
        },
		{
            "fieldname": "membership_type",
            "fieldtype": "Link",
            "label": "Membership Type",
            "options": "Memberships Type"
        },
		{
            "fieldname": "membership_plan",
            "fieldtype": "Link",
            "label": "Membership Plan",
            "options": "Memberships Plan"
        },
	]
};
