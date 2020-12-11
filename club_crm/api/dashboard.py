import frappe
from frappe.utils import now_datetime
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_dashboard_details(client_id):
    valet = frappe.get_all('Valet Parking', filters={'client_id': client_id,'status': 'Parked'}, fields=['name','date','client_id','client_name','membership_status','membership_id','vehicle_no','vehicle_type','location','parking_time','modified_by'])
    frappe.response["message"] = {
        "Valet": valet
         }