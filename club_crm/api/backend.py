from __future__ import unicode_literals
import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist(allow_guest=True)
def login(usr,pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] ={
                "success_key":0,
                "message":"Authentication Failed"
                }
        return
    frappe.errprint(frappe.session)
    api_generate=generate_keys(frappe.session.user)
    roles = frappe.get_roles()
    user=frappe.get_doc('User',frappe.session.user)
    frappe.clear_messages()
    frappe.response["message"]={
            "success_key":1,
            "sid": frappe.session.sid,
            "User Details":{"Email":user.name,"Full Name":user.full_name,"Is employee":user.is_employee,"Gender":user.gender,"Mobile No":user.mobile_no,"api key":user.api_key},
            "api secret":api_generate,
            "Roles":roles
            }
    return

def generate_keys(user):
    user_details = frappe.get_doc("User", user)
    api_secret = frappe.generate_hash(length=15)
    # if api key is not set generate api key
    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
    user_details.api_secret = api_secret
    user_details.save()
    return api_secret
