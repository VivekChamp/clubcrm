from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	if filters:
		columns = get_column()
		data = get_data(filters)
	return columns, data
def get_column():
	columns = [
	{
	"label": "Application Type",
	"fieldname": "application_type",
	"fieldtype": "Data",
	"width": 150
	},
	{
	"label": "Voucher No",
	"fieldname": "voucher_no",
	"fieldtype": "Dynamic Link",
	"options":"application_type",
	"width": 150
	},
	{
	"label": "Client ID",
	"fieldname": "client_id",
	"fieldtype": "Link",
	"options":"Client",
	"width": 150
	},
	{
	"label": "Client Name",
	"fieldname": "client_name",
	"fieldtype": "Data",
	"width": 200
	},
	{
	"label": "Member ID",
	"fieldname": "member_id",
	"fieldtype": "Data",
	"width": 100
	},
	{
	"label": "Payment Mode",
	"fieldname": "in_payment_mode",
	"fieldtype": "Data",
	"width": 100
	},
	{
	"label": "Amount",
	"fieldname": "in_amount",
	"fieldtype": "Currency",
	"width": 160
	}
	]
	return columns

def get_data(filters):
	data =[]
	final_data =[]
	filter_data = []
	mem_app_list = frappe.db.sql('''select %s as application_type, ma.name as voucher_no,
						ma.client_id as client_id, ma.first_name_1 as client_name,
						cp.mode_of_payment as in_payment_mode, 
						cp.paid_amount as in_amount
						from `tabMemberships Application` ma join `tabCart Payment` cp
						on cp.parent = ma.name
						where ma.application_date between %s and %s and ma.docstatus = 1''',
						('Memberships Application',filters['from_date'],filters['to_date']), as_dict = True)

	ftr = frappe.db.sql('''select %s as application_type, ftr.name as voucher_no, ftr.membership_status,
						ftr.client_id as client_id, ftr.client_name as client_name,
						cp.mode_of_payment as in_payment_mode, cp.paid_amount as in_amount
						from `tabFitness Training Request` ftr join `tabCart Payment` cp
						on cp.parent = ftr.name
						where ftr.date between %s and %s''',
						('Fitness Training Request',filters['from_date'],filters['to_date']), as_dict = True)

	on_order = frappe.db.sql('''select %s as application_type, ord.name as voucher_no, ord.membership_status,
						ord.client_id as client_id, ord.client_name as client_name, 
						ord.total_amount as in_amount, ord.payment_method as in_payment_mode
						from `tabOnline Order` ord
						where ord.created_date between %s and %s and ord.payment_status = "Paid"''',
						('Online Order',filters['from_date'],filters['to_date']), as_dict = True)

	cart = frappe.db.sql('''select %s as application_type, ca.name as voucher_no, ca.membership_status, ca.products_check,
						ca.client_id as client_id, ca.client_name as client_name, ca.sessions_check,
						cp.mode_of_payment as in_payment_mode, cp.paid_amount as in_amount 
						from `tabCart` ca join `tabCart Payment` cp
						on cp.parent = ca.name
						where ca.date between %s and %s ''',
						('Cart',filters['from_date'],filters['to_date']), as_dict = True)
	
	if 'application_type' in filters:
		if filters['application_type'] in ['Spa','Fitness','Club']:
			for row in cart:
				if 'sessions_check' in row and row['sessions_check']:
					in_amount = frappe.db.get_value('Cart Session',{'parent': row['voucher_no'],'package_type': filters['application_type']},'total_price')
					if in_amount:
						row['in_amount'] = in_amount
						data.append(row)
				if 'appoinment_check' in row and row['appoinment_check']:
					in_amount = frappe.db.get_value('Cart Appoinment',{'parent': row['voucher_no'],'package_type': ['in', ['Spa']]},'total_price')
					if in_amount:
						row['in_amount'] = in_amount

		if filters['application_type'] == 'Fitness Training Request':
			data += ftr
		if filters['application_type'] == 'Retail':
			for row in cart:
				if row['products_check']:
					data.append(row)
		if filters['application_type'] == 'Membership':
			data += mem_app_list
	else:
		for row in cart:
			if 'sessions_check' in row and row['sessions_check']:
				in_amount = frappe.db.get_value('Cart Session',{'parent': row['voucher_no'],'package_type': ['in', ['Spa','Fitness','Club']]},'total_price')
				if in_amount:
					row['in_amount'] = in_amount
			if 'appoinment_check' in row and row['appoinment_check']:
				in_amount = frappe.db.get_value('Cart Appoinment',{'parent': row['voucher_no'],'package_type': ['in', ['Spa']]},'total_price')
				if in_amount:
					row['in_amount'] = in_amount

		data = ftr + mem_app_list + cart + on_order

	for row in data:
		allow_by_membership_status = False
		allow_by_payment_type = False
		if 'client_id' in row:
			row['member_id'] = frappe.db.get_value('Client', row['client_id'], 'member_id')
			row['membership_status'] = frappe.db.get_value('Client', row['client_id'], 'membership_status')
		if 'membership_status' in filters:
			if filters['membership_status'] == row['membership_status']:
				allow_by_membership_status = True
		else:
			allow_by_membership_status = True

		if 'payment_type' in filters:
			if filters['payment_type'] == 'Online' and row['in_payment_mode'] == 'Online Payment':
				allow_by_payment_type = True
			elif filters['payment_type'] == 'Offline' and row['in_payment_mode'] != 'Online Payment':
				allow_by_payment_type = True
			else:
				allow_by_payment_type = False
		else:
			allow_by_payment_type = True
		if allow_by_membership_status and allow_by_payment_type:
			filter_data.append(row)
	
	for row in filter_data:
		if row['in_amount'] != 0.00:
			final_data.append(row)
	
	return final_data
