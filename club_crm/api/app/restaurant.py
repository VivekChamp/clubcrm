from __future__ import unicode_literals
import frappe
import datetime
import time
import re
from datetime import datetime, timedelta
from datetime import datetime, date
from frappe.utils import escape_html
from frappe import throw, msgprint, _
from club_crm.api.wallet import get_balance

@frappe.whitelist()
def reservation(client_id,no_of_people,date,start_time):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    dt = date+" "+start_time
    starttime = datetime.strptime(dt, "%d-%m-%Y %H:%M")
    endtime= starttime + timedelta(minutes=60)
    doc = frappe.get_doc({
        'doctype': 'Grams Reservation',
        'client_id': client.name,
        'status': 'Pending',
        'no_of_people':no_of_people,
        'reservation_time': starttime,
        'reservation_end_time': endtime
        })
    doc.insert()
    doc.submit()
    frappe.response["message"] = {
        "Name": doc.name,
        "Status":1,
        "Status Message": "Reservation submitted successfully"
        }

@frappe.whitelist()         
def get_status(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_all('Grams Reservation', filters={'client_id':client.name,'status': "Pending"}, fields=["*"])
    if doc:
        frappe.response["message"] = {
            "Status": 0,
            "Status Message": "Pending"
            }
    else:
        doc= frappe.get_all('Grams Reservation', filters={'client_id':client.name,'status': "Scheduled"}, fields=["*"])
        if doc:
            doc_1= doc[0]
            frappe.response["message"] = {
            "Status":1,
            "Status Message": "Scheduled",
            "From Time": doc_1.reservation_time,
            "To Time": doc_1.reservation_end_time
            }

@frappe.whitelist()         
def get_time(date):
    date_1 = str(date)
    day_name = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    day = day_name[datetime.strptime(date_1, '%d-%m-%Y').weekday()]

    doc = frappe.get_doc('Grams Schedule')
    slots = doc.time_slots

    time_slot=[]
    for days in slots:
        if days.day==day and days.disabled==0:
            time_slot.append(days.from_time)
    return time_slot

@frappe.whitelist()         
def cancel_reservation(client_id):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc= frappe.get_all('Grams Reservation', filters={'client_id':client.name,'status': ['in',{'Pending', 'Scheduled'}], 'docstatus':1})
    if doc:
        doc_1=doc[0]
        frappe.db.set_value('Grams Reservation', doc_1.name, {
            'docstatus': 2,
            'status': 'Cancelled'
            })
        frappe.response["message"] = {
            "status": 1,
            "status_message":"Table Reservation Cancelled"
            }

@frappe.whitelist()         
def get_menu_categories():
    doc= frappe.get_all('Item Group', filters={'parent_item_group':'Restaurant'}, fields=['name','image'], order_by="item_group_name asc")
    return doc

# Remove after app update
@frappe.whitelist()         
def get_menu_item(category):
    doc= frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'], order_by="item_name asc")
    if doc:
        menu = []
        for d in doc:
            price = frappe.get_all('Item Price', filters={'item_code':d.item_code, 'price_list':'Grams Menu'}, fields=['*'])
            if price:
                price_1=price[0]
                description = re.sub("<.*?>", "", price_1.item_description)
                menu.append({
                    "item_code": d.item_code,
                    "item_name": d.item_name,
                    "item_group": d.item_group,
                    "image": d.image,
                    "description": description,
                    "currency": price_1.currency,
                    "rate": format(price_1.price_list_rate, '.2f')
                })
            
        frappe.response["message"] = {
            "status": 1,
            "status_message": "Product Details",
            "item": menu
        }

    else:
        frappe.response["message"] = {
            "status": 0,
            "status_message": "No products available for this category"
        }

@frappe.whitelist()         
def get_menu_items(category):
    doc= frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'], order_by="item_name asc")
    if doc:
        menu = []
        for d in doc:
            price = frappe.get_all('Item Price', filters={'item_code':d.item_code, 'price_list':'Grams Menu'}, fields=['*'])
            if price:
                price_1=price[0]
                description = re.sub("<.*?>", "", price_1.item_description)
                menu.append({
                    "item_code": d.item_code,
                    "item_name": d.item_name,
                    "item_group": d.item_group,
                    "image": d.image,
                    "description": description,
                    "currency": price_1.currency,
                    "rate": format(price_1.price_list_rate, '.2f'),
                    "prep_time": d.preperation_time
                })
            
        frappe.response["message"] = {
            "status": 1,
            "status_message": "Product Details",
            "item": menu
        }

    else:
        frappe.response["message"] = {
            "status": 0,
            "status_message": "No products available for this category"
        }

@frappe.whitelist()         
def add_to_cart(client_id, item_code, qty):
    today = date.today()
    client = frappe.db.get("Client", {"email": frappe.session.user})
    cart= frappe.get_list('Food Order Entry', filters={'client_id':client.name, 'date': today, 'order_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc= frappe.get_doc('Food Order Entry', cart_1.name)
        doc.append('order_items', {
            'item': item_code,
            'qty':qty
            })
        doc.save()
        return doc
    
    else:
        doc = frappe.get_doc({
            'doctype':'Food Order Entry',
            'client_id': client.name,
            'order_items': [{
            'item': item_code,
            'qty':qty
            }]
        })
        doc.insert()
        return doc

@frappe.whitelist()         
def delete_from_cart(document_name,item_document_name):
    cart= frappe.get_doc('Food Order Entry', document_name)
    row= None
    for d in cart.order_items:
        if d.name==item_document_name:
            row = d
            cart.remove(row)
            cart.save()
            frappe.db.commit()

    if cart.order_items:
        frappe.response["message"] = {
            "status": 1,
            "document_name": cart.name,
            "date": cart.date,
            "payment_status": cart.payment_status,
            "client_id": cart.client_id,
            "total_quantity": cart.total_quantity,
            "total_amount": cart.total_amount,
            "items": cart.order_items
        }
    else:
        frappe.db.set_value('Food Order Entry', cart.name, {
            'docstatus':2,
            'order_status': 'Cancelled'
        })
        frappe.db.commit()
        frappe.response["message"] = {
            "status": 0
        }

@frappe.whitelist()         
def get_cart(client_id):
    today = date.today()
    client = frappe.db.get("Client", {"email": frappe.session.user})
    cart= frappe.get_list('Food Order Entry', filters={'client_id':client.name, 'date': today, 'order_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc= frappe.get_doc('Food Order Entry', cart_1.name)
        frappe.response["message"] = {
            "status": 1,
            "document_name": doc.name,
            "date": doc.date,
            "payment_status": doc.payment_status,
            "client_id": doc.client_id,
            "total_quantity": doc.total_quantity,
            "total_amount": doc.total_amount,
            "items": doc.order_items
        }
    else:
        frappe.response["message"] = {
            "status": 0
        }

@frappe.whitelist()
def cart_checkout(payment_method, order_type):
    today = date.today()
    client = frappe.db.get("Client", {"email": frappe.session.user})
    cart= frappe.get_list('Food Order Entry', filters={'client_id': client.name, 'date': today, 'order_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc= frappe.get_doc('Food Order Entry', cart_1.name)
        doc.payment_method = payment_method
        doc.order_type = order_type
        doc.save()
        
    wallet= get_balance()
    frappe.response["message"] = {
        "status": 1,
        "document_name": doc.name,
        "cart_status": doc.order_status,
        "payment_status": doc.payment_status,
        "client_name": doc.client_name,
        "total_quantity": doc.total_quantity,
        "total_amount": doc.total_amount,
        "wallet_balance": wallet
        }

@frappe.whitelist()
def checkout(client_id, payment_method):
    today = date.today()
    client = frappe.db.get("Client", {"email": frappe.session.user})
    cart= frappe.get_list('Food Order Entry', filters={'client_id': client.name, 'date': today, 'order_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc= frappe.get_doc('Food Order Entry', cart_1.name)
        doc.payment_method = payment_method
        doc.save()
        
    wallet= get_balance()
    frappe.response["message"] = {
        "status": 1,
        "document_name": doc.name,
        "cart_status": doc.order_status,
        "payment_status": doc.payment_status,
        "client_name": doc.client_name,
        "total_quantity": doc.total_quantity,
        "total_amount": doc.total_amount,
        "wallet_balance": wallet
        }