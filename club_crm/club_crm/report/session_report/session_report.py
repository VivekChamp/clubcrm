
from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe import _

def execute(filters=None):
	columns, query = [], []
	columns = get_columns(filters)
	query = get_data(filters)
	return columns, query

def get_columns(filters):
	columns = [
		{
            'fieldname': 'client_id',
            'label': _('Client ID'),
            'fieldtype': 'Link',
            'options': 'Client'
        },
		_("Client Name") + ":Data:250",
		_("Member ID") + "::80",
		_("Session Status") + "::90",
		_("Start Date") + ":Date:100",
		_("Expiry Date") + ":Date:110",
		_("Package Name") + ":Data:250",
		_("Service Type") + "::110",
		_("Service Name") + "::100",
		_("Membership Status") + ":Data:100",
		_("Total Sessions") + "::80",
		_("Booked Sessions") + "::80",
		_("Used Sessions") + "::80",
		_("Remaining Sessions") + "::80"
	]
	
	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select
								ses.client_id,
								ses.client_name,
								ses.member_id,
								ses.session_status,
								ses.start_date,
								ses.expiry_date,
								ses.package_name,
								ses.service_type,
								ses.service_name,
								ses.membership_status,
								ses.total_sessions,
								ses.booked_sessions,
								ses.used_sessions,
								ses.remaining_sessions

								FROM `tabClient Sessions` ses
								where ses.session_status != 'Cancelled' %s """ % 
								conditions, filters, as_dict=1)
				
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get('membership_status'): conditions += "  and ses.membership_status = %(membership_status)s"
	if filters.get('package_name'): conditions += "  and ses.package_name = %(package_name)s"
	if filters.get('service_type'): conditions += "  and ses.service_type = %(service_type)s"
	if filters.get('service_name'): conditions += "  and ses.service_name = %(service_name)s"
	
	return conditions