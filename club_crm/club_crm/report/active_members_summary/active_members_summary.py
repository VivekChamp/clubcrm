# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta, date, time
from frappe.utils import getdate, add_to_date, get_time, flt
from frappe import _

def execute(filters=None):
	if not filters: filters = {}
	today = getdate()

	if filters.get("expiry_in"):
		if filters.get("expiry_in") == "30 Days":
			new_date = add_to_date(today, days=30)
		if filters.get("expiry_in") == "45 Days":
			new_date = add_to_date(today, days=45)
		if filters.get("expiry_in") == "60 Days":
			new_date = add_to_date(today, days=60)
		if filters.get("expiry_in") == "90 Days":
			new_date = add_to_date(today, days=90)
		if filters.get("expiry_in") == "Custom Days":
			day = 0
			if filters.get("expiry_days"):
				day += int(filters.get("expiry_days"))
			new_date = add_to_date(today, days=int(day))
		filters['new_date'] = new_date

	if filters.get("mem_duration"):
		if filters.get("mem_duration") == "1 month":
			month = 1
		if filters.get("mem_duration") == "3 months":
			month = 3
		if filters.get("mem_duration") == "6 months":
			month = 6
		if filters.get("mem_duration") == "12 months":
			month = 12
		filters['duration'] = month
	
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": "ID",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Client",
			"width": 100
		},
		{
			"label": "Client Name",
			"fieldname": "client_name",
			"fieldtype": "Data",
			"width": 275
		},
		{
			"label": "Member ID",
			"fieldname": "member_id",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Card No",
			"fieldname": "card_no",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Gender",
			"fieldname": "gender",
			"fieldtype": "Data",
			"width": 80
		},
		{
			"label": "CEC",
			"fieldname": "assigned_to",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Membership Plan",
			"fieldname": "membership_plan",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": "Start Date",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": "Expiry Date (Actual)",
			"fieldname": "actual_expiry_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Expiry Date (with extension)",
			"fieldname": "expiry_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Nationality",
			"fieldname": "nationality",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Birth Date",
			"fieldname": "birth_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": "Qatar ID",
			"fieldname": "qatar_id",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Mobile No",
			"fieldname": "mobile_no",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Email",
			"fieldname": "email",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": "Occupation",
			"fieldname": "occupation",
			"fieldtype": "Data",
			"width": 150
		}
	]

	return columns

def get_data(filters):
	data= []
	conditions = get_conditions(filters)

	query = frappe.db.sql("""select
								client.name, client.client_name, client.member_id, client.card_no, client.gender,
								client.assigned_to, client.nationality, client.birth_date, client.qatar_id,
								client.mobile_no, client.email, client.occupation, mem.membership_category,
								mem.membership_type, mem.membership_plan, mem.start_date, mem.actual_expiry_date,
								mem.expiry_date

							from `tabClient` client
							left join `tabMembership History` memh
								on client.name = memh.parent
							left join `tabMemberships` mem
								on memh.membership = mem.name
							left join `tabMemberships Plan` memp
								on mem.membership_plan = memp.name

							where
								memh.status = 'Active' %s """ %
							conditions, filters, as_dict=1)

	return query

def get_conditions(filters):
	conditions = ""
	if filters.get('gender'): conditions += "and client.gender = %(gender)s"
	if filters.get('nationality'): conditions += " and client.nationality = %(nationality)s"
	if filters.get('assigned_to'): conditions += " and client.assigned_to = %(assigned_to)s"
	if filters.get('reg_on_app'): conditions += " and client.reg_on_app = %(reg_on_app)s"
	if filters.get('vaccination_status'): conditions += " and client.vaccination_status = %(vaccination_status)s"
	if filters.get("occupation_sector"): conditions += " and client.occupation_sector = %(occupation_sector)s"
	if filters.get("membership_category"): conditions += " and mem.membership_category = %(membership_category)s"
	if filters.get("membership_type"): conditions += " and mem.membership_type = %(membership_type)s"
	if filters.get("membership_plan"): conditions += " and mem.membership_plan = %(membership_plan)s"
	if filters.get("mem_duration"): conditions += " and memp.duration_months = %(duration)s"
	if filters.get("expiry_in"): conditions += " and mem.expiry_date < %(new_date)s"

	return conditions