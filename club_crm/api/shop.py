from __future__ import unicode_literals
import frappe
import dateutil
import re
from frappe.utils import getdate
from frappe.model.document import Document
from frappe import throw, msgprint, _

@frappe.whitelist()
def get_category():
    shop_category = frappe.get_all('Item Group', filters={'parent_item_group': "Retail Inventory"}, fields=['name','image'])
    frappe.response["message"] = {
        "Shop Categories": shop_category
         }

@frappe.whitelist()         
def get_product(client_id,category):
    client= frappe.get_doc('Client', client_id)
    if client.membership_status=="Member":
        mem= frappe.get_list('Member Benefits', filters={'client_id':client_id, 'benefit_status':'Active'}, fields=['*'])
        if mem:
            mem_1=mem[0]
            discount = int(mem_1.retail)
            
            doc= frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'])
            if doc:
                product=[]
                for d in doc:
                    price= frappe.get_all('Item Price', filters={'item_code':d.item_code, 'price_list':'Standard Selling'}, fields=['*'])
                    if price:
                        price_1=price[0]
                        description = re.sub("<.*?>", "", price_1.item_description)
                        reg_price= int(price_1.price_list_rate)
                        member_price= reg_price - (reg_price * discount/100.0)
                        product.append({
                            "item_code": d.item_code,
                            "item_name": d.item_name,
                            "item_group": d.item_group,
                            "image": d.image,
                            "description": description,
                            "currency": price_1.currency,
                            "regular_price": format(reg_price, '.2f'),
                            "member_price": format(member_price, '.2f')
                        })
                frappe.response["message"] = {
                    "status": 1,
                    "status_message": "Product Details",
                    "item": product
                }
            else:
                frappe.response["message"] = {
                    "status": 0,
                    "status_message": "No products available for this category"
                }
    else:
        doc= frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'])
        if doc:
                product=[]
                for d in doc:
                    price= frappe.get_all('Item Price', filters={'item_code':d.item_code, 'price_list':'Standard Selling'}, fields=['*'])
                    if price:
                        price_1=price[0]
                        description = re.sub("<.*?>", "", price_1.item_description)
                        reg_price= int(price_1.price_list_rate)
                        product.append({
                            "item_code": d.item_code,
                            "item_name": d.item_name,
                            "item_group": d.item_group,
                            "image": d.image,
                            "description": description,
                            "currency": price_1.currency,
                            "regular_price": format(reg_price, '.2f')
                        })
                frappe.response["message"] = {
                    "status": 1,
                    "status_message": "Product Details",
                    "item": product
                }
        else:
                frappe.response["message"] = {
                    "status": 0,
                    "status_message": "No products available for this category"
                }

@frappe.whitelist()         
def add_to_cart(client_id, item_code, qty):
    cart= frappe.get_list('Online Order', filters={'client_id':client_id, 'cart_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc= frappe.get_doc('Online Order', cart_1.name)
        doc.append('item', {
            'item_code': item_code,
            'quantity':qty
            })
        doc.save()
        return doc
        
    else:
        doc = frappe.get_doc({
            'doctype':'Online Order',
            'client_id': client_id,
            'item': [{
            'item_code': item_code,
            'quantity':qty
            }]
        })
        doc.insert()
        return doc

@frappe.whitelist()         
def delete_from_cart(document_name,item_document_name):
    cart= frappe.get_doc('Online Order', document_name)
    row= None
    for d in cart.item:
        if d.name==item_document_name:
            row = d
            cart.remove(row)
            cart.save()
            frappe.db.commit()

    if cart.item:
        frappe.response["message"] = {
            "status": 1,
            "document_name": cart.name,
            "date": cart.created_date,
            "payment_status": cart.payment_status,
            "client_id": cart.client_id,
            "total_amount": cart.total_amount,
            "items": cart.item
        }
    else:
        cart.submit()
        frappe.db.set_value('Online Order', cart.name, {
            'docstatus':2,
            'cart_status': 'Cancelled'
        })
        frappe.db.commit()
        frappe.response["message"] = {
            "status": 0
        }


@frappe.whitelist()         
def get_cart(client_id):
    cart= frappe.get_list('Online Order', filters={'client_id':client_id, 'cart_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc= frappe.get_doc('Online Order', cart_1.name)
        frappe.response["message"] = {
            "status": 1,
            "document_name": doc.name,
            "date": doc.created_date,
            "payment_status": doc.payment_status,
            "client_id": doc.client_id,
            "total_amount": doc.total_amount,
            "items": doc.item
        }
    else:
        frappe.response["message"] = {
            "status": 0
        }

@frappe.whitelist()         
def checkout(document_name):
    doc= frappe.get_doc('Online Order', document_name)
    doc.submit()
    return doc