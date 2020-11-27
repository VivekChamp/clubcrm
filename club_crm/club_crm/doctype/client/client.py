from __future__ import unicode_literals
import frappe
import dateutil
from frappe.utils import getdate
from frappe.model.document import Document

class Client(Document):
    def validate(self):
            self.set_full_name()
            self.get_age()

    def set_full_name(self):
		    if self.last_name:
			        self.client_name = ' '.join(filter(None, [self.first_name, self.last_name]))
		    else:
			        self.client_name = self.first_name
    
    def get_age(self):
		    if self.birth_date:
			        birth_date = getdate(self.birth_date)
			        age = dateutil.relativedelta.relativedelta(getdate(), birth_date)
			        age_html = str(age.years) + ' year(s) ' + str(age.months) + ' month(s) ' + str(age.days) + ' day(s)'
		    self.age_html = age_html

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

