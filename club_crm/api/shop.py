from __future__ import unicode_literals
import frappe
import dateutil
from frappe.utils import getdate
from frappe.model.document import Document
from frappe import throw, msgprint, _
from erpnext.shopping_cart.cart import _get_cart_quotation, _set_price_list
from erpnext.shopping_cart.doctype.shopping_cart_settings.shopping_cart_settings \
	import get_shopping_cart_settings, show_quantity_in_website
from erpnext.utilities.product import get_price, get_qty_in_stock, get_non_stock_item_status

@frappe.whitelist()
def get_category():
    shop_category = frappe.get_all('Item Group', filters={'parent_item_group': "Retail Inventory"}, fields=['name','image'])
    frappe.response["message"] = {
        "Shop Categories": shop_category
         }

@frappe.whitelist()
def get_product(shop_category):
    shop_product = frappe.get_all('Item', filters={'item_group':shop_category}, fields=['name'])
    for name in shop_product:
        price= get_product_info_for_website(name)
        return price

    frappe.response["message"] = {
        "Shop Categories": shop_product
         }