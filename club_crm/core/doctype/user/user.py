from __future__ import unicode_literals, print_function
import frappe
from frappe.model.document import Document

def create_client_user(doc, method=None):
    #user = frappe.get_last_doc('User')
    client = frappe.get_all('Client', filters={'mobile_no':doc.mobile_no}, fields={'name','birth_date','email'})

    if not client:
        if doc.is_employee==0:
            d = frappe.get_doc(dict(
                doctype= 'Client',
                first_name= doc.first_name,
                last_name= doc.last_name,
                client_name= doc.full_name,
                gender= doc.gender,
                birth_date= doc.birth_date,
                status= "Active",
                membership_status= "Non-Member",
                reg_on_app= "Yes",
                qatar_id= doc.qatar_id,
                mobile_no= doc.mobile_no,
                email= doc.email,
                default_currency='QAR', 
                ))
            d.insert()
            d.save()

        else:
            frappe.response["message"] = "Employee Created"   
    else:
        for t in client:
            #client_doc = name
            d = frappe.get_doc('Client', t.name)
            d.email= doc.email
            d.reg_on_app= "Yes"
            d.save()
