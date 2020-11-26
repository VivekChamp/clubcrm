import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_spa_category():
    spa_category = frappe.get_all('Spa Menu Category', filters={'on_app': 1}, fields=['spa_category_name','category_image'])
    frappe.response["message"] = {
        "Spa Categories": spa_category
         }

@frappe.whitelist()
def get_spa_item(spa_category):
    spa_item = frappe.get_all('Spa Menu', filters={'spa_menu_category':spa_category,'on_app': 1,'disabled':0},fields=['spa_item_name','spa_menu_group','spa_menu_category','duration','rate','has_addon','description','image'])
    frappe.response["message"] = {
        "Spa Items": spa_item
        }
