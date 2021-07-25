# Copyright (c) 2013, Blue Lynx and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	columns = [
		_("Date") + ":Date:100",
		_("Name") + ":Data:120",
		_("Client Name") + "::250",
		_("Appointments") + ":Currency:110",
		_("Sessions") + ":Currency:110",
		_("Retail") + ":Currency:110",
		_("Tips") + ":Currency:110",
		_("Discounts") + ":Currency:110",
		_("Grand Total") + ":Currency:125"
	]

	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select
								cart.date,
								cart.name,
								cart.client_name,
								cart.net_total_appointments,
								cart.net_total_sessions,
								cart.net_total_products,
								cart.total_tips,
								cart.discount_amount,
								cart.grand_total
							
							from `tabCart` cart

							where cart.docstatus<2 and cart.payment_status = 'Paid' %s """ % 
							conditions, filters, as_dict=1)
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get('date'): conditions += "and cart.date = %(date)s"

	return conditions