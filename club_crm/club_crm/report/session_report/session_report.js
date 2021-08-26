// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Session Report"] = {
	"filters": [

		{
            'fieldname': "membership_status",
            'label': "Membership Status",
            'fieldtype': "Select",
            'options': "\nMember\nNon-Member"
        },
        {
            'fieldname': "package_name",
            'label': "Package Name",
            'fieldtype': "Link",
            'options': "Club Packages",
            'depends_on': "eval: doc.membership_status == 'Member'"
        },
        {
            'fieldname': "service_type",
            'label': "Service Type",
            'fieldtype': "Select",
            'options': "\nSpa Services\nClub Services\nFitness Services",
            'depends_on': "eval: doc.membership_status == 'Member'"
        },
	]
};
