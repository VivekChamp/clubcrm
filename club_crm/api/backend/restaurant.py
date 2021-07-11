from __future__ import unicode_literals
import frappe
from datetime import datetime, date
from club_crm.club_crm.utils.sms_notification import send_sms
from club_crm.club_crm.utils.push_notification import send_push
from frappe.utils import getdate, get_time, flt
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def todays_order():
    today = date.today()

    orders = []
    order_list =  frappe.get_all('Food Order Entry', filters={'date': today, 'order_status':['in', {'Ordered','Ready', 'Delivered'}]}, fields=['*'])
    if order_list:
        for each_order in order_list:
            order = frappe.get_doc('Food Order Entry', each_order.name)
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
                'order_id': order.name,
                'client_name': order.client_name,
                'order_status': order.order_status,
                'mobile_no': order.mobile_number,
                'total_quantity': order.total_quantity,
                'total_amount': order.total_amount,
                'order_type': order.order_type,
                'items': items
            })
    
    frappe.response["message"] = {
      "orders": orders
    }

@frappe.whitelist()
def order_ready(order_id):
    order = frappe.get_doc('Food Order Entry', order_id)
    frappe.db.set_value("Food Order Entry",order_id,"order_status","Ready")
    frappe.db.commit()

    if order.ready_notify==0:
        client = frappe.get_doc('Client', order.client_id)
        msg = "Your food order from Grams is ready."
        receiver_list='"'+str(order.mobile_number)+'"'
        send_sms(receiver_list,msg)
        
        if client.fcm_token:
            title = "Grams at Katara Club"
            send_push(client.name,title,msg)
            frappe.db.set_value("Food Order Entry",order_id,"ready_notify",1)
            frappe.db.commit()

    order = frappe.get_doc('Food Order Entry', order_id)
    items = []
    if order.order_items:
        for row in order.order_items:
            items.append({
                'item_name': row.item_name,
                'qty': row.qty,
                'rate': row.rate,
                'amount': row.amount
            })

    frappe.response["message"] = {
        'status': 1,
        'status_message': 'Order is marked as Ready',
        'order_id': order.name,
        'client_name': order.client_name,
        'order_status': order.order_status,
        'mobile_no': order.mobile_number,
        'total_quantity': order.total_quantity,
        'total_amount': order.total_amount,
        'order_type': order.order_type,
        'items': items
    }

@frappe.whitelist()
def order_delivered(order_id):
    order = frappe.get_doc('Food Order Entry', order_id)
    frappe.db.set_value("Food Order Entry",order_id,"order_status","Delivered")
    frappe.db.commit()

    order = frappe.get_doc('Food Order Entry', order_id)
    items = []
    if order.order_items:
        for row in order.order_items:
            items.append({
                'item_name': row.item_name,
                'qty': row.qty,
                'rate': row.rate,
                'amount': row.amount
            })

    frappe.response["message"] = {
        "status": 1,
        "status_message": 'Order is marked as Delivered',
        'order_id': order.name,
        'client_name': order.client_name,
        'order_status': order.order_status,
        'mobile_no': order.mobile_number,
        'total_quantity': order.total_quantity,
        'total_amount': order.total_amount,
        'order_type': order.order_type,
        'items': items
    }