from __future__ import unicode_literals, print_function
import frappe
from frappe.model.document import Document

def create_client_user(*args, **newargs):
    user = frappe.get_last_doc('User')
    user_mobile_no = user.mobile_no
    client = frappe.get_all('Client', filters={'mobile_no':user_mobile_no}, fields=['name','birth_date','email'])

    if not client:
        if user.is_employee==0:
            doc = frappe.get_doc(dict(
                doctype= 'Client',
                first_name= user.first_name,
                last_name= user.last_name,
                client_name= user.full_name,
                gender= user.gender,
                birth_date= user.birth_date,
                status= "Active",
                membership_status= "Non-Member",
                reg_on_app= "Yes",
                qatar_id= user.qatar_id,
                mobile_no= user.mobile_no,
                email= user.email
                ))
            doc.insert()

        else:
            frappe.response["message"] = "Employee Created"   
    else:
        for name in client:
            client_doc = name
            doc = frappe.get_doc('Client', client_doc.name)
            doc.email= user.email
            doc.reg_on_app= "Yes"
            doc.save()
