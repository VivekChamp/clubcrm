from __future__ import unicode_literals
import frappe
import dateutil
from frappe.utils import getdate
from frappe.model.document import Document
from frappe.utils import comma_and
from frappe import _

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

    def after_insert(self):
        customer = frappe.get_all('Customer', filters={'mobile_no':self.mobile_no})
        if not customer:
            self.create_customer()

    # def on_update(self):
    #     user = frappe.get_doc('User', self.email)
    #     user.first_name= self.first_name
    #     user.last_name= self.last_name
    #     user.mobile_no = self.mobile_no
    #     user.gender= self.gender
    #     user.save()
    
    def on_trash(self):
        user_doc = frappe.db.get_value('User', {'mobile_no':self.mobile_no, 'email': self.email}, 'name')
        if self.reg_on_app == 'Yes':
            if user_doc:
                frappe.throw(_(f'Unable to delete this client as it is linked with the user {0}').format(comma_and(
                    """<a href="#Form/User/{0}">{1}</a>""".format(user_doc, user_doc))))
        if self.reg_on_app == 'No':
            if user_doc:
                frappe.delete_doc('User', user_doc)

    def create_customer(self):
        customer = frappe.get_doc({
            'doctype': 'Customer',
            'customer_name': self.client_name,
            'client_type': 'Club Client',
            'customer_group': 'Clients',
            'territory' : 'Qatar',
            'gender': self.gender,
            'email_id': self.email,
            'client_id': self.name,
            'so_required':1,
            'dn_required':1,
            'customer_type': 'Individual',
        }).insert(ignore_permissions=True,ignore_mandatory=True)
        frappe.db.set_value('Client', self.name, {
            'customer': customer.name,
            'customer_group': customer.customer_group,
            'territory': customer.territory
        })

def create_customer_client(doc, method=None):
    customer = frappe.get_all('Customer', filters={'mobile_no':doc.mobile_no})
    if not customer:
        d = frappe.get_doc(dict(
            doctype= 'Customer',
            customer_name= doc.client_name,
            client_type= 'Club Client',
            customer_group= 'Clients',
            territory= 'Qatar',
            gender=doc.gender,
            email_id= doc.email,
            mobile_no=doc.mobile_no,
            client_id=doc.name,
            so_required=1,
            dn_required=1,
            customer_type='Individual' 
            ))
        d.insert()
        frappe.db.set_value('Client', d.name, {
            'customer': d.name,
            'customer_group': d.customer_group,
            'territory': d.territory
            },update_modified=False)

