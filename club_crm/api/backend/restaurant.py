from __future__ import unicode_literals
import frappe
from datetime import datetime, date
from frappe.utils import getdate, get_time, flt
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def todays_order():
    today = date.today()

    orders = []
    order_list =  frappe.get_all('Food Order Entry', filters={'date': today, 'order_status':['in', {'Ordered','Ready', 'Delivered'}]}, fields=['*'])
    if order_list:
        for order in order_list:
            items = []
            if order.order_items:
                for row in order.order_items:
                    items.append({
                        'item_name': row.item_name,
                        'qty': row.qty,
                        'rate': row.rate,
                        'amount': row.amount
                    })
            orders.append({
                'client_name': order.client_name,
                'order_status': order.order_status,
                'mobile_no': order.mobile_no,
                'total_quantity': order.total_quantity,
                'total_amount': order.total_amount,
                'items': items
            })
    
    frappe.response["message"] = {
      "orders": orders
    }
