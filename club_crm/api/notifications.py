import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_status():
    client = frappe.db.get("Client", {"email": frappe.session.user})
    frappe.response["message"] = {
        "offers": client.offers_notification
    }

@frappe.whitelist()
def set_notifications(offers):
    client = frappe.db.get("Client", {"email": frappe.session.user})

    frappe.db.set_value("Client", client.name, "offers_notification",offers)
    frappe.db.commit()

    frappe.response["message"] = {
        "offers": client.offers_notification
    }