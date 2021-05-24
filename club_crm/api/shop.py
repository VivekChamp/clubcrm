from __future__ import unicode_literals
import frappe
import dateutil
import re
import numpy as np
from frappe.utils import getdate
from frappe.model.document import Document
from frappe import throw, msgprint, _
from club_crm.club_crm.doctype.cart.cart import add_cart_from_shop_online
from club_crm.api.wallet import get_balance

@frappe.whitelist()
def get_category():
    shop_category = frappe.get_all('Item Group', filters={'parent_item_group': "Retail Inventory", 'show_on_app':1}, fields=['name','image'])
    frappe.response["message"] = {
        "Shop Categories": shop_category
         }

@frappe.whitelist()         
def get_products(category,count):
    client = frappe.db.get("Client", {"email": frappe.session.user})

    product = []
    if client.membership_status == "Member":
        discount = 0.0
        memberships = frappe.get_all('Memberships', filters={'membership_id': client.membership_id, 'membership_status':'Active'}, fields=['*'])
        if memberships:
            for mem in memberships:
                discount = mem.retail_discount
            
                items = frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'])
                if items:
                    for item in items:
                        price = frappe.get_all('Item Price', filters={'item_code':item.item_code, 'price_list':'Standard Selling'}, fields=['*'])
                        if price:
                            price_1 = price[0]
                            description = re.sub("<.*?>", "", price_1.item_description)
                            reg_price = price_1.price_list_rate
                            mem_price = reg_price - (reg_price * discount/100.0)
                            member_price = mem_price//0.5*0.5
                            product.append({
                                "item_code": item.item_code,
                                "item_name": item.item_name,
                                "item_group": item.item_group,
                                "image": item.image,
                                "description": description,
                                "currency": price_1.currency,
                                "regular_price": format(reg_price, '.2f'),
                                "member_price": format(member_price, '.2f')
                            })

    else:
        items = frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'])
        if items:
            for item in items:
                price = frappe.get_all('Item Price', filters={'item_code':item.item_code, 'price_list':'Standard Selling'}, fields=['*'])
                if price:
                    price_1 = price[0]
                    description = re.sub("<.*?>", "", price_1.item_description)
                    reg_price= price_1.price_list_rate
                    product.append({
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "item_group": item.item_group,
                        "image": item.image,
                        "description": description,
                        "currency": price_1.currency,
                        "regular_price": format(reg_price, '.2f')
                    })
    if product:
        total_count = len(product)
        frappe.response["message"] = {
            "status": 1,
            "status_message": "Product Details",
            "total_count": total_count,
            "item": product[int(count):int(count)+16]
    }
    else:
        frappe.response["message"] = {
            "status": 0,
            "status_message": "No products available for this category"
        }

@frappe.whitelist()         
def get_product(client_id,category):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    # client = frappe.get_doc('Client', client_id)
    if client.membership_status == "Member":
        discount = 0.0
        memberships = frappe.get_all('Memberships', filters={'membership_id': client.membership_id, 'membership_status':'Active'}, fields=['*'])
        if memberships:
            for mem in memberships:
                discount = mem.retail_discount
            
                items = frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'])
                if items:
                    product = []
                    for item in items:
                        price = frappe.get_all('Item Price', filters={'item_code':item.item_code, 'price_list':'Standard Selling'}, fields=['*'])
                        if price:
                            price_1 = price[0]
                            description = re.sub("<.*?>", "", price_1.item_description)
                            reg_price = float(price_1.price_list_rate)
                            member_price = float(reg_price) - float(reg_price * discount/100.0)
                            product.append({
                                "item_code": item.item_code,
                                "item_name": item.item_name,
                                "item_group": item.item_group,
                                "image": item.image,
                                "description": description,
                                "currency": price_1.currency,
                                "regular_price": reg_price,
                                "member_price": member_price
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
        items = frappe.get_all('Item', filters={'item_group':category, 'disabled': 0}, fields=['*'])
        if items:
            product=[]
            for item in items:
                price = frappe.get_all('Item Price', filters={'item_code':item.item_code, 'price_list':'Standard Selling'}, fields=['*'])
                if price:
                    price_1 = price[0]
                    description = re.sub("<.*?>", "", price_1.item_description)
                    reg_price= price_1.price_list_rate
                    product.append({
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "item_group": item.item_group,
                        "image": item.image,
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
    discount = 0.0
    client = frappe.db.get("Client", {"email": frappe.session.user})
    doc = frappe.get_doc('Client', client.name)
    if doc.membership_status == "Member":
        if doc.membership_history:
            for row in doc.membership_history:
                if row.status == "Active":
                    mem = frappe.get_doc('Memberships', row.membership)
                    discount = mem.retail_discount
                    
    price_list = frappe.get_all('Item Price', filters={'item_code':item_code, 'price_list':'Standard Selling'}, fields=['*'])
    if price_list:
        for price in price_list:
            item_price = price.price_list_rate

    carts = frappe.get_all('Online Order', filters={'client_id':client.name, 'cart_status': 'Cart'})
    if carts:
        for cart in carts:
            doc = frappe.get_doc('Online Order', cart.name)
            doc.append('item', {
                'item_code': item_code,
                'quantity':qty,
                'rate': item_price,
                'discount': discount
            })
            doc.save()

            # items = []
            # for item in doc.item:
            #     items.append({
            #         'name': item.name,
            #         'parent': item.parent,
            #         'item_code': item.item_code,
            #         'item_name': item.item_name,
            #         'quantity': int(item.quantity),
            #         'rate': int(item.rate),
            #         # 'discount': item.discount,
            #         'amount': int(item.amount)
            #     })

            frappe.response["message"] = {
                'name': doc.name,
                'client_id': doc.client_id,
                'client_name': doc.client_name,
                'mobile_number': doc.mobile_number,
                'membership_status': doc.membership_status,
                'cart_status': doc.cart_status,
                'payment_status': doc.payment_status,
                'payment_method': doc.payment_method,
                'total_quantity': int(doc.total_quantity),
                'total_amount': doc.total_amount,
                'naming_series': doc.naming_series,
                'doctype': doc.doctype,
                'item': doc.item
            }
    else:
        doc = frappe.get_doc({
            'doctype':'Online Order',
            'client_id': client.name,
            'item': [{
                'item_code': item_code,
                'quantity':qty,
                'rate': item_price,
                'discount': discount
            }]
        })
        doc.save()

        # items = []
        # for item in doc.item:
        #     items.append({
        #         'name': item.name,
        #         'parent': item.parent,
        #         'item_code': item.item_code,
        #         'item_name': item.item_name,
        #         'quantity': item.quantity,
        #         'rate': int(item.rate),
        #         # 'discount': item.discount,
        #         'amount': int(item.amount)
        #     })
        frappe.response["message"] = {
                'name': doc.name,
                'client_id': doc.client_id,
                'client_name': doc.client_name,
                'mobile_number': doc.mobile_number,
                'membership_status': doc.membership_status,
                'cart_status': doc.cart_status,
                'payment_status': doc.payment_status,
                'payment_method': doc.payment_method,
                'total_quantity': int(doc.total_quantity),
                'total_amount': doc.total_amount,
                'naming_series': doc.naming_series,
                'doctype': doc.doctype,
                'item': doc.item
            }

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
            "total_quantity": cart.total_quantity,
            "total_amount": cart.total_amount,
            "items": cart.item
        }
    else:
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
    client = frappe.db.get("Client", {"email": frappe.session.user})
    cart= frappe.get_list('Online Order', filters={'client_id': client.name, 'cart_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc= frappe.get_doc('Online Order', cart_1.name)
        items = []
        for item in doc.item:
            items.append({
                'name': item.name,
                'parent': item.parent,
                'parentfield': item.parentfield,
                'item_code': item.item_code,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'rate': item.amount
            })
        frappe.response["message"] = {
            "status": 1,
            "document_name": doc.name,
            "date": doc.created_date,
            "payment_status": doc.payment_status,
            "client_id": doc.client_id,
            "total_quantity": doc.total_quantity,
            "total_amount": doc.total_amount,
            "items": items
        }
    else:
        frappe.response["message"] = {
            "status": 0
        }

@frappe.whitelist()
def checkout(client_id, payment_method):
    client = frappe.db.get("Client", {"email": frappe.session.user})

    cart = frappe.get_list('Online Order', filters={'client_id': client.name, 'cart_status': 'Cart'}, fields=['*'])
    if cart:
        cart_1=cart[0]
        doc = frappe.get_doc('Online Order', cart_1.name)
        doc.cart_status = 'Check-out'
        doc.payment_method = payment_method
        doc.save()

    to_cart = add_cart_from_shop_online(doc.client_id, doc.name)

    wallet = get_balance()
    frappe.response["message"] = {
        "status": 1,
        "document_name": to_cart.name,
        "cart_status": doc.cart_status,
        "payment_status": doc.payment_status,
        "client_name": doc.client_name,
        "total_quantity": to_cart.total_quantity,
        "total_amount": to_cart.grand_total,
        "wallet_balance": wallet
        }