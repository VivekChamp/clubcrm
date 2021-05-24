import frappe
from erpnext.selling.doctype.sms_center.sms_center import SMSCenter

class CustomSMSCenter(SMSCenter):
	@frappe.whitelist()
	def create_receiver_list(self):
		super(CustomSMSCenter, self).create_receiver_list()
		if self.send_to == 'All Members':
			rec = frappe.db.sql("""select client_name, mobile_no from `tabClient` where 
				ifnull(mobile_no,'')!='' and docstatus != 2 and membership_status='Member'""")
		
		elif self.send_to == 'All Non-Members':
			rec = frappe.db.sql("""select client_name, mobile_no from `tabClient` where
				ifnull(mobile_no,'')!='' and docstatus != 2 and membership_status='Non-Member'""")

		elif self.send_to == 'All Clients':
			rec = frappe.db.sql("""select client_name, mobile_no from `tabClient` where 
				ifnull(mobile_no,'')!='' and docstatus != 2""")

		elif self.send_to == 'All Employee (Active)':
			where_clause = self.department and " and department = '%s'" % \
				self.department.replace("'", "\'") or ""
			where_clause += self.branch and " and branch = '%s'" % \
				self.branch.replace("'", "\'") or ""
			
			rec = frappe.db.sql("""select employee_name, cell_number from
				`tabEmployee` where status = 'Active' and docstatus < 2 and
				ifnull(cell_number,'')!='' %s""" % where_clause)

		rec_list = ''
		for d in rec:
			rec_list += d[0] + ' : ' + d[1] + '\n'
		self.receiver_list = rec_list
