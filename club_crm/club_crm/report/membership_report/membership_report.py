from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, query = [], []
	columns = get_columns(filters)
	query = get_data(filters)
	return columns, query

def get_columns(filters):
	columns = [
		_("Primary Client ID") + ":Data:250",
		_("Primary Client Name") + "::80",
		_("Member ID") + "::90",
		_("Membership Plan") + ":Data:110",
		_("Memberships Type") + ":Data:100",
		_("Membership Category") + ":Data:100",
		_("Membership Type") +":Data:100",
	]

	# if filters.get('membership_type') == "Family Membership":
	# 	columns.insert(8, _("Client ID") + ":Data:220"),
	# 	columns.insert(9, _("Client  Name") + ":Data:100")

	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select 
								mem.primary_client_id,
								mem.primary_client_name,
								mem.membership_id,
								mem.membership_plan,
								mem.memberships_type,
								mem.membership_category,
								mem.membership_type
							FROM `tabMemberships` mem
							where mem.membership_status != 'Cancelled' %s """ % 
							conditions, filters, as_dict=1)
							
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get("membership_type"): conditions += " and mem.membership_type = %(membership_type)s"
	if filters.get('memberships_type'): conditions += "and mem.memberships_type = %(memberships_type)s"
	return conditions

