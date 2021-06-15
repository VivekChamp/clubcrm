from __future__ import unicode_literals
import frappe
from club_crm.api.wallet import get_balance
from frappe.utils import escape_html
from frappe import throw, msgprint, _
import math, random
from frappe.core.doctype.sms_settings.sms_settings import send_sms

@frappe.whitelist(allow_guest=True)
def login(usr,pwd):
        try:
            login_manager = frappe.auth.LoginManager()
            login_manager.authenticate(user=usr,pwd=pwd)
            login_manager.post_login()
        except frappe.exceptions.AuthenticationError:
            frappe.clear_messages()
            frappe.local.response["message"] =  {
                "success_key":0,
                "message":"Authentication Failed"
                }
            return
        api_generate = generate_keys(frappe.session.user)
        user = frappe.get_doc('User',frappe.session.user)
        if user.is_employee == 0:
            pg = frappe.get_doc('CS Settings')
            client_details = []

            client = frappe.db.get("Client", {"email": frappe.session.user})
            client_details.append({
                'name': client.name,
                'first_name': client.first_name,
                'last_name': client.last_name,
                'client_name': client.client_name,
                'gender': client.gender,
                'birth_date': client.birth_date,
                'nationality': client.nationality,
                'qatar_id': client.qatar_id,
                'email': client.email,
                'mobile_no': client.mobile_no,
                'apply_membership': client.apply_membership,
                'mem_application': client.mem_application,
                'membership_status': client.membership_status,
                'status': client.status,
                'customer_group': client.customer_group,
                'territory': client.territory ,
                'marital_status': client.marital_status,
                'image': client.image
            })

            wallet = get_balance()
            frappe.response["message"] = {
                "sid": frappe.session.sid,
                "client details": client_details,
                "api_key":user.api_key,
                "api secret": api_generate,
                "wallet_balance": wallet,
                "access_key": pg.access_key,
                "profile_id": pg.profile_id,
                "transaction_url": pg.transaction_url,
                "base_url": pg.base_url
            }
        else:
            frappe.local.response["message"] =  {
                "success_key":0,
                "message":"Authentication Failed"
            }

def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)
    # if api key is not set generate api key
    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
    user_details.api_secret = api_secret
    user_details.save()
    return api_secret

@frappe.whitelist(allow_guest=True)
def user_sign_up(email, first_name, last_name, gender, birth_date, qatar_id, mobile_no, password):
    user = frappe.db.get("User", {"email": email})
    if user:
        if user.enabled==0:
            return 0, _("Registered but disabled")
        else:
            return 0, _("Already Registered")
    else:   
        user = frappe.get_doc({
            "doctype":"User",
            "email": email,
            "first_name": escape_html(first_name),
            "last_name": escape_html(last_name),
            "gender": escape_html(gender),
            "birth_date": birth_date,
            "qatar_id":qatar_id,
            "mobile_no": mobile_no,
            "enabled": 1,
            "new_password": password,
            "send_welcome_email":0,
            "send_password_update_notification":0,
            "user_type": "Website User"
            })
        user.flags.ignore_permissions = True
        user.flags.ignore_password_policy = True
        user.insert()
        # set default signup role as per Portal Settings
        default_role = frappe.db.get_value("Portal Settings", None, "default_role")
        if default_role:
            user.add_roles(default_role)
        user.save()
        return 1, _("success")
			
@frappe.whitelist(allow_guest=True)
def check_user(email, mobile_no):

    email = frappe.db.get("User", {"email": email})
    mobile = frappe.db.get("User", {"mobile_no": mobile_no})
    
    if email:
        if mobile:
            return "User is already registered"
        else:
            return "User is already registered"
    else:
        if mobile:
            return "User is already registered"
        else:
            return "User does not exist"

@frappe.whitelist(allow_guest=True)
def forgot_password(mobile_no, new_password):
    doc = frappe.get_all('User', filters={'mobile_no':mobile_no}, fields=["*"])
    if doc:
        for d in doc:
            user = frappe.get_doc('User', d.email)
            user.new_password = new_password
            user.save()
            frappe.response["message"] = {
                "Status": "1",
                "Description":"Password reset success"
            }
    else:
        frappe.response["message"] = {
            "Status": "0",
            "Description":"User does not exist"
        }

@frappe.whitelist(allow_guest=True)
def generate_otp(mobile_no):
    digits = "0123456789"
    OTP = "" 
    for i in range(6): 
        OTP += digits[math.floor(random.random() * 10)]
    msg = "Your verification code is "+OTP+". Do not share it with anyone."
    receiver_list='"'+mobile_no+'"'
    send_sms(receiver_list,msg)
    return OTP

@frappe.whitelist(allow_guest=True)
def generate_otp_email(mobile_no, email):
    digits = "0123456789"
    OTP = "" 
    for i in range(6): 
        OTP += digits[math.floor(random.random() * 10)]
    msg = "Your verification code is "+OTP+". Do not share it with anyone."
    receiver_list='"'+mobile_no+'"'
    send_sms(receiver_list,msg)

    if email:
        email_id = email
    else:
        client_list = frappe.get_all('Client', filters={'mobile_no': mobile_no}, fields=['name', 'mobile_no', 'email'])
        if client_list:
            for client in client_list:
                email_id = client.email

    message = "Dear Valued Guest,<br><br>"
    message += "Thank you for using the Katara Club app.<br>"
    message += "Your verification code is <br><br>"
    message += "<b>{0}</b><br><br>".format(OTP)
    message += "Please do not share this code with anyone else.<br><br>"
    message += "If you did not initiate this request, please contact us on 44081580.<br>"
    message += "We look forward to seeing you at the Club.<br><br>"
    message += "Sincerely,<br>"
    message += "The Katara Club Team"

    frappe.sendmail(
		recipients = email_id,
		subject = "Katara Club verification",
		message = message,
        now=True
	)
    return OTP