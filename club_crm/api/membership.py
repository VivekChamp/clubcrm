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
    countries = frappe.get_all('Country', fields=['name'])
    nationality = []
    nationality.append({'name': 'Qatar'})
    for country in countries:
        if not country.name == 'Qatar':
            nationality.append(country)

    frappe.response["message"] = nationality

@frappe.whitelist()
def member_benefits(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_doc('Client', client.name)

    if doc.membership_status == 'Member':
        if doc.membership_history:
            for row in doc.membership_history:
                if row.status == "Active":
                    mem = frappe.get_doc('Memberships', row.membership)
                    spa_discount = int(mem.spa_discount)
                    retail_discount = int(mem.retail_discount)
                    grams_discount = 0
                    boho_discount = 20
                    salon_discount = 15
        else:
            spa_discount = 0
            retail_discount = 0
            grams_discount = 0
            boho_discount = 0
            salon_discount = 0
        
        benefits = []
        ben = frappe.get_all('Client Sessions', filters={'client_id':doc.name, 'package_type':'Club', 'session_status' : 'Active'}, fields=['*'])
        for comp in ben:
            benefits.append({
                "benefits_name" : comp.title,
                "count": "Limited",
                "quantity": str(comp.total_sessions),
                "used": str(comp.used_sessions),
                "remaining": str(comp.remaining_sessions)
            })

        mem = frappe.get_all('Memberships', filters={'client_id_1': doc.name, 'membership_status': 'Active'}, fields=['*'])

        if mem:
            mem_1 = mem[0]
            frappe.response["message"] = {
                    'status': 1,
                    'membership_status': 'Member',
                    'client_name': doc.name,
                    'member_id': doc.member_id,
                    'membership': doc.membership_id,
                    'start_date': mem_1.start_date,
                    'expiry_date': mem_1.expiry_date,
                    'spa_discount': spa_discount,
                    'retail_discount': retail_discount,
                    'grams_discount': grams_discount,
                    'boho_discount': boho_discount,
                    'salon_discount': salon_discount,
                    'benefits': benefits
            }
        else:
            frappe.response["message"] = {
                'status': 0,
                'membership_status': 'Non-Member'
            }
    else:
        frappe.response["message"] = {
            'status': 0,
            'membership_status': 'Non-Member'
        }