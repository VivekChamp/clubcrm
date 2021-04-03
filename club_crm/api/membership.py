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
    membership_plan = frappe.get_all('Memberships Plan', filters={'membership_type':membership_type,'on_app': 1}, fields=['membership_plan_name','joining_fee_adult','membership_fee_adult','membership_fee_child'])
    mem_plan = []
    for plan in membership_plan:
        mem_plan.append({
            "membership_plan_name" : plan.membership_plan_name,
            "joining_fee" : plan.joining_fee_adult,
            "mem_fee_adult" : plan.membership_fee_adult,
            "mem_fee_kid" : plan.membership_fee_child
        })
    frappe.response["message"] = {
            "Membership Plans": mem_plan
            }

@frappe.whitelist()
def nationality():
    nationality = frappe.get_all('Country', fields=['name'])
    frappe.response["message"] = nationality

@frappe.whitelist()
def member_benefits(client_id):
    doc = frappe.get_doc('Client', client_id)
    if doc.membership_status == 'Member':
        spa_treatments = 25.0
        retail = 15.0
        grams = 20.0
        boho_social = 20.0
        salon = 15.0
        
        ben = frappe.get_all('Client Sessions', filters={'client_id':client_id, 'package_type':'Club', 'session_status' : 'Active'}, fields=['*'])

        mem = frappe.get_all('Memberships', filters={'client_id': client_id, 'membership_status': 'Active'}, fields=['*'])
        if mem:
            mem_1 = mem[0]
            frappe.response["message"] = {
                    'status': 1,
                    'membership_status': 'Member',
                    'client_name': client_id,
                    'member_id': doc.member_id,
                    'membership': doc.membership_id,
                    'start_date': mem_1.start_date,
                    'expiry_date': mem_1.expiry_date,
                    'spa_discount': spa_treatments,
                    'retail_discount': retail,
                    'grams_discount': grams,
                    'boho_discount': boho_social,
                    'salon_discount': salon,
                    'benefits': ben
                }
    else:
        frappe.response["message"] = {
                'status': 0,
                'membership_status': 'Non-Member'
            }