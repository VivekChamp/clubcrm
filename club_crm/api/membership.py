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
    membership_plan = frappe.get_all('Memberships Plan', filters={'membership_type':membership_type,'on_app': 1}, fields=['membership_plan_name','joining_fee','mem_fee_adult','mem_fee_kid'])
    frappe.response["message"] = {
            "Membership Plans": membership_plan
            }

@frappe.whitelist()
def nationality():
    nationality = frappe.get_all('Country', fields=['name'])
    frappe.response["message"] = nationality

@frappe.whitelist()
def member_benefits(client_id):
    doc= frappe.get_doc('Client', client_id)
    if doc.membership_status=='Member':
        ben= frappe.get_all('Member Benefits', filters={'client_id':client_id, 'benefit_status':'Active'}, fields=['*'])
        ben_1=ben[0]
        mem_ben= frappe.get_doc('Member Benefits', ben_1.name)
        benefits=frappe.get_all('Member Benefits Item', filters={'parent':ben_1.name,'parentfield':'benefits'}, fields=['benefits_name','count','quantity','used','remaining'])
        frappe.response["message"] = {
                'status': 1,
                'membership_status': 'Member',
                'client_name': mem_ben.client_id,
                'member_id': mem_ben.member_id,
                'membership': mem_ben.membership,
                'start_date': mem_ben.start_date,
                'expiry_date': mem_ben.expiry_date,
                'spa_discount': mem_ben.spa_treatments,
                'retail_discount': mem_ben.retail,
                'grams_discount': mem_ben.grams,
                'boho_discount': mem_ben.boho_social,
                'salon_discount': mem_ben.salon,
                'benefits': benefits
            }
    else:
        frappe.response["message"] = {
                'status': 0,
                'membership_status': 'Non-Member'
            }