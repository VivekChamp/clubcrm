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
		_("ID") + ":Link/Client:100",
		_("Client Name") + ":Data:275",
		_("Gender") + ":Data:80",
		_("Nationality") + ":Data:100",
		_("Mem Status") + ":Data:100",
		_("Birth Date") + ":Date:100",
		_("Qatar ID") + ":Data:110",
		_("Mobile No") + ":Data:100",
		_("Email") + ":Data:150",
		_("Occupation") + ":Data:150",
		_("Marital Status") + ":Data:100"
	]

	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select
								client.name as id,
								client.client_name,
								client.gender,
								client.nationality,
								client.membership_status as mem_status,
								client.birth_date,
								client.qatar_id,
								client.mobile_no,
								client.email,
								client.occupation,
								client.marital_status
							
							from `tabClient` client

							where client.docstatus<2 %s
							order by client.name""" %
							conditions, filters, as_dict=1)
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get('gender'): conditions += "and client.gender = %(gender)s"
	if filters.get('nationality'): conditions += " and client.nationality = %(nationality)s"
	if filters.get('reg_on_app'): conditions += " and client.reg_on_app = %(reg_on_app)s"
	if filters.get('membership_status'): conditions += "  and client.membership_status = %(membership_status)s"
	if filters.get('vaccination_status'): conditions += " and client.vaccination_status = %(vaccination_status)s"
	if filters.get("occupation_sector"): conditions += " and client.occupation_sector = %(occupation_sector)s"

	return conditions
