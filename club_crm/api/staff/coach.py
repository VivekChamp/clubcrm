import frappe
from datetime import date, time, datetime, timedelta
from frappe.website.utils import is_signup_enabled
from frappe.utils import escape_html
from frappe import throw, msgprint, _

@frappe.whitelist()
def package_requests():
    doc = frappe.get_all('Service Staff',filters={'email':frappe.session.user})
    if doc:
        for d in doc:
            pending = frappe.get_list('Fitness Training Request', filters={'trainer':d.name, 'request_status':['in',{'Scheduled','Pending'}]}, fields=['*'])
            requests=[]
            for t in pending:
                package=frappe.get_doc('Fitness Training Request', t.name)
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

@frappe.whitelist()
def trainer_schedule(from_date,to_date):
    doc= frappe.get_all('Service Staff',filters={'email':frappe.session.user})
    if doc:
        for d in doc:
            startdate = datetime.strptime(from_date, "%Y-%m-%d")
            end = datetime.strptime(to_date, "%Y-%m-%d")
            enddate = end + timedelta(1)

            schedule = frappe.get_all('Fitness Training Appointment', filters={'service_staff':d.name, 'appointment_status':['not in',{'Cancelled'}], 'start_time':['between', [startdate, enddate]]}, fields=['name','date','client_id','client_name','mobile_number','package_name','start_time','end_time'])
            count= len(schedule)
            if schedule:
                frappe.response["message"] = {
                "status": 1,
                "count": count,
                "schedule": schedule
                }
            else:
                frappe.response["message"] = {
                    "status": 0
                }
    else:
        frappe.response["message"] = {
                    "status": 2
                }
