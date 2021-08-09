// Copyright (c) 2016, Blue Lynx and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Active Members Summary"] = {
    "filters": [{
            'fieldname': "membership_category",
            'label': "Membership Category",
            'fieldtype': "Link",
            'options': "Memberships Category"
        },
        {
            'fieldname': "membership_type",
            'label': "Membership Type",
            'fieldtype': "Link",
            'options': "Memberships Type"
        },
        {
            'fieldname': "membership_plan",
            'label': "Membership Plan",
            'fieldtype': "Link",
            'options': "Memberships Plan",
            get_query: () => {
                var type = frappe.query_report.get_filter_value('membership_type');
                var category = frappe.query_report.get_filter_value('membership_category');
                if (type && !category) {
                    return {
                        filters: {
                            'membership_type': type
                        }
                    };

                }
                if (!type && category) {
                    return {
                        filters: {
                            'membership_category': category
                        }
                    };

                }

                if (type && category) {
                    return {
                        filters: {
                            'membership_type': type,
                            'membership_category': category
                        }
                    };
                }
            }
        },
        {
            'fieldname': "mem_duration",
            'label': "Membership Duration",
            'fieldtype': "Select",
            'options': "\n1 month\n3 months\n6 months\n12 months"
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
            "fieldname": "vaccination_status",
            "fieldtype": "Select",
            "label": "Vaccination Status",
            "options": "\nVaccinated\nFirst shot\nNot vaccinated\nNo info"
        },
        {
            "fieldname": "expiry_in",
            "fieldtype": "Select",
            "label": "Expiring in",
            "options": "\n30 Days\n45 Days\n60 Days\n90 Days\nCustom Days"
        },
        {
            "fieldname": "expiry_days",
            "fieldtype": "Data",
            "label": "Days",
            "depends_on": "eval:doc.expiry_in=='Custom Days'"
        }
    ]
};