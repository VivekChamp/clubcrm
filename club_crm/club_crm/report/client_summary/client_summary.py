# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	columns = [
		_("Client Name") + ":Data:250",
		_("Gender") + "::80",
		_("Nationality") + "::90",
		_("Birth Date") + ":Date:100",
		_("Qatar ID") + ":Data:110",
		_("Mobile No") + ":Data:100",
		_("Assigned To") + ":Data:100"
	]

	if filters.get('membership_status') == "Member":
		columns.insert(8, _("Membership Plan") + ":Data:220"),
		columns.insert(9, _("Start Date") + ":Data:100"),
		columns.insert(10, _("End Date") + ":Data:100")

	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select
								client.client_name,
								client.gender,
								client.nationality,
								client.birth_date,
								client.qatar_id,
								client.mobile_no,
								client.assigned_to,
								id.membership_plan,
								id.start_date,
								id.end_date
							
							from `tabClient` client
							left join `tabMembership History` id on id.parent = client.name

							where client.docstatus<2 %s """ % 
							conditions, filters, as_dict=1)
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get('gender'): conditions += "and client.gender = %(gender)s"
	if filters.get('nationality'): conditions += " and client.nationality = %(nationality)s"
	if filters.get('reg_on_app'): conditions += " and client.reg_on_app = %(reg_on_app)s"
	if filters.get('membership_status'): conditions += "  and client.membership_status = %(membership_status)s"
	if filters.get('assigned_to'): conditions += " and client.assigned_to = %(assigned_to)s"
	if filters.get('vaccination_status'): conditions += " and client.vaccination_status = %(vaccination_status)s"
	if filters.get('vaccination_status'): conditions += " and client.vaccination_status = %(vaccination_status)s"
	if filters.get("membership_plan"): conditions += " and id.membership_plan = %(membership_plan)s"

	return conditions