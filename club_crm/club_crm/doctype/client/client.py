from __future__ import unicode_literals
import frappe
import dateutil
from frappe.utils import getdate
from frappe.model.document import Document

class Client(Document):
    def after_insert(self):
        customer = frappe.get_all('Customer', filters={'mobile_no':self.mobile_no})
        if not customer:
            self.create_customer()
    
    def validate(self):
        self.set_full_name()
        self.get_age()
        self.set_membership_status()

    def set_full_name(self):
        if self.last_name:
            client_name = ' '.join(filter(None, [self.first_name, self.last_name]))
        else:
            client_name = self.first_name
        self.client_name = client_name.title()
    
    def get_age(self):
        if self.birth_date:
            birth_date = getdate(self.birth_date)
            age = dateutil.relativedelta.relativedelta(getdate(), birth_date)
            age_html = str(age.years) + ' year(s) ' + str(age.months) + ' month(s) ' + str(age.days) + ' day(s)'
            self.age_html = age_html

    def set_membership_status(self):
        self.membership_status = "Non-Member"
        if self.membership_history:
            for row in self.membership_history:
                if row.status == "Active":
                    self.membership_status = "Member"

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

@frappe.whitelist()
def check_status(client_id):
    client = frappe.get_doc('Client', client_id)
    return client.status

@frappe.whitelist()
def auto_checkout():
    client_list = frappe.get_all('Client', filters={'status':'Checked-in'})
    if client_list:
        for client in client_list:
            frappe.db.set_value('Client', client.name, 'status', 'Active')
            frappe.db.commit()


@frappe.whitelist()
def benefits(client_id):
    benefit = []
    benefit.append(['Benefit Name', 'Remaining', 'Expiry Date', 'Status'])
    ben = frappe.get_all('Client Sessions', filters={'client_id':client_id, 'package_type':'Club'}, fields=['*'])
    for comp in ben:
        expiry_date = comp.expiry_date.strftime("%d-%m-%Y")
        benefit.append([comp.title, str(comp.remaining_session_text), str(expiry_date), comp.session_status])
    frappe.msgprint(benefit, title="Benefits List", as_table=True)

@frappe.whitelist()
def medical_history(client_id,allergies,medication,history,notes):
    client = frappe.db.get("Client", {"email": frappe.session.user})
    client.allergies = allergies
    client.medication = medication
    client.medical_history = history
    client.other_notes = notes
    client.save()
    frappe.response["message"] =  {
		"Status": 1
    }

@frappe.whitelist()
def create_missing_customers():
    client_list = frappe.get_all('Client')
    for clients in client_list:
        client = frappe.get_doc('Client', clients.name)
        if client.email:
            email = client.email
        else:
            email = None
        if not client.customer:
            doc = frappe.get_doc({
            'doctype': 'Customer',
            'customer_name': client.client_name,
            'client_type': 'Club Client',
            'customer_group': 'Clients',
            'territory' : 'Qatar',
            'gender': client.gender,
            'email_id': email,
            'client_id': client.name,
            'so_required':1,
            'dn_required':1,
            'customer_type': 'Individual',
            })
            doc.insert(ignore_permissions=True,ignore_mandatory=True)

            frappe.db.set_value('Client', client.name, {
                'customer': doc.name,
                'customer_group': doc.customer_group,
                'territory': doc.territory
            })
            frappe.db.commit()