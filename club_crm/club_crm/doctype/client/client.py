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
    
    # def after_insert(self):
    #     doc = frappe.get_doc({
    #         'doctype': 'Customer',
    #         'customer_name': self.client_name,
    #         'client_type': 'Club Client',
    #         'gender': self.gender,
    #         'email_id': self.email,
    #         'client_id': self.name,
    #         'customer_type': 'Individual',
    #         'customer_group': 'Clients',
    #         'territory': 'Qatar',
    #         'so_required':1,
    #         'dn_required':1
    #     })
    #     doc.insert()
    #     doc.save()

    def on_update(self):
        d = self.get_doc_before_save()
        if not self.customer:
        #     customer = frappe.get_all('Customer', filters={'email_id':self.email})
        #     if customer:
        #         for t in customer:
        #             t.customer_name = self.client_name
        #             t.save()
        # else:
            create_customer(self)

        user = frappe.get_doc('User', d.email)
        user.first_name= self.first_name
        user.last_name= self.last_name
        user.mobile_no = self.mobile_no
        user.gender= self.gender
        user.save()
    
    def on_trash(self):
        user= frappe.get_doc('User', self.email)
        user.delete()

def create_customer(doc):
	customer = frappe.get_doc({
		'doctype': 'Customer',
		'customer_name': doc.client_name,
        'client_type': 'Club Client',
		'customer_group': "Clients",
		'territory' : "Qatar",
        'gender': doc.gender,
        'email_id': doc.email,
        'client_id': doc.name,
        'so_required':1,
        'dn_required':1,
		'customer_type': 'Individual',
	}).insert(ignore_permissions=True, ignore_mandatory=True)
	frappe.db.set_value('Client', doc.name, 'customer', customer.name)
	frappe.msgprint(_('Customer {0} is created.').format(customer.name), alert=True)

    
