import frappe
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def trainer_schedule(email):
    doc= frappe.get_all('Fitness Trainer',filters={'email':email})
    doc_1=doc[0]
    schedule= frappe.get_all('Fitness Training Appointment', filters={'trainer_id':doc_1.name, 'status':['in',{'Scheduled','Open'}]}, fields=['name','date','client_id','client_name','mobile_number','package_name','start_time','end_time'])
    return schedule

@frappe.whitelist()
def package_requests(email):
    doc= frappe.get_all('Fitness Trainer',filters={'email':email})
    doc_1=doc[0]
    pending= frappe.get_all('Fitness Training Request', filters={'trainer':doc_1.name, 'request_status':['in',{'Scheduled','Pending'}],'docstatus':1}, fields=['*'])
    requests=[]
    for name in pending:
        package=frappe.get_doc('Fitness Training Request', name.name)
        customer=package.customer_preference
        dates=[]
        for count in customer:
            dates.append({
                'day': count.day,
                'time':count.client_session
            })
        requests.append({
            'name':package.name,
            'date':package.date,
            'request_status':package.request_status,
            'client_id':package.client_id,
            'client_name':package.client_name,
            'mobile_number': package.mobile_number,
            'gender': package.gender,
            'fitness_package': package.fitness_package,
            'no_of_sessions': package.number_of_sessions,
            'price': package.price,
            'start_day': package.start_date,
            'payment_status': package.payment_status,
            'customer_preference':dates
            })
    return requests