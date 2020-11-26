import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def membership_type():
    membership_type = frappe.get_all('Memberships Type', filters={'on_app': 1}, fields=['membership_type_name'])
    frappe.response["message"] = {
            "Membership Types": membership_type
            }

@frappe.whitelist()
def membership_plan(membership_type):
    membership_plan = frappe.get_all('Memberships Plan', filters={'membership_type':membership_type,'on_app': 1}, fields=['membership_plan_name','joining_fee','membership_fee'])
    frappe.response["message"] = {
            "Membership Plans": membership_plan
            }

