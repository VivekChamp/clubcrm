from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Client(Document):
    pass

def create_customer_client(*args, **newargs):
    client = frappe.get_last_doc('Client')
    doc = frappe.get_doc({
        'doctype': 'Customer',
        'customer_name': client.client_name,
        'gender': client.gender,
        'email_id': client.email,
        'customer_type': "Individual",
        'customer_group': "Clients",
        'territory': "Qatar",
        'so_required':1,
        'dn_required':1
        })
    doc.insert()
    client_update = frappe.get_last_doc('Customer')
    client.customer= client_update.name
    client.save()
