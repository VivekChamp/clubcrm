import frappe
from datetime import datetime, date
from frappe.utils import now_datetime
from frappe.utils import escape_html
from frappe import throw, msgprint, _


@frappe.whitelist()
def get_saved_cards():
    client = frappe.db.get("Client", {"email": frappe.session.user})
    cards_list = frappe.get_all('Card Token', filters={'client_id': client.name})
    saved_cards = []
    if cards_list:
        for cards in cards_list:
            card = frappe.get_doc('Card Token', cards.name)
            saved_cards.append({
                'name': card.name,
                'card_name': card.token_name,
                'expiry_date': card.card_expiry_date
            })
        
        frappe.response["message"] = {
        "status": 1,
        "cards": saved_cards
        }

    else:
        frappe.response["message"] = {
        "status": 0,
        "cards": saved_cards
        }