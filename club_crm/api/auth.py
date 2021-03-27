import frappe
from frappe.website.utils import is_signup_enabled
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
    api_generate=generate_keys(frappe.session.user)
    user = frappe.get_doc('User',frappe.session.user)
    # pg = frappe.get_doc('CS Settings')
    client_details = frappe.get_all('Client', filters={'mobile_no': usr}, fields=['name','first_name','last_name','client_name','gender','birth_date','nationality','qatar_id','email','mobile_no','apply_membership','mem_application','membership_status','status','customer_group','territory','marital_status','image'])
    if client_details:
        d = client_details[0]
        wallet= get_balance(d.name)
        frappe.response["message"] =	{
            "sid": frappe.session.sid,
            "client details": client_details,
            "api_key":user.api_key,
            "api secret": api_generate,
            "wallet_balance": wallet,
            # "access_key": pg.access_key,
            # "profile_id": pg.profile_id,
            # "transaction_url": pg.transaction_url
            }
    else:
        frappe.response["message"] =	{
            "sid": frappe.session.sid,
            "client details": [],
            "api_key":user.api_key,
            "api secret": api_generate
            }

        return

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
    if not is_signup_enabled():
        frappe.throw(_('Sign Up is disabled'), title='Not Allowed')
        
    user = frappe.db.get("User", {"email": email})
    if user:
        if user.disabled:
            return 0, _("Registered but disabled")
        else:
            return 0, _("Already Registered")
    else:
        if frappe.db.sql("""select count(*) from tabUser where HOUR(TIMEDIFF(CURRENT_TIMESTAMP, TIMESTAMP(modified)))=1""")[0][0] > 300:
            frappe.respond_as_web_page(_('Temporarily Disabled'),
	_('Too many users signed up recently, so the registration is disabled. Please try back in an hour'),
        http_status_code=429)
        
    from frappe.utils import random_string
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
        "send_welcome_mail":0,
        "send_password_update_notification":0,
        "user_type": "Website User"
        })
    user.flags.ignore_permissions = True
    user.flags.ignore_password_policy = True
    user.insert()
    user.new_password=password
    user.save()
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
        user = doc[0]
        frappe.db.set_value("User",user.name,"new_password",new_password)
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
    for i in range(5): 
        OTP += digits[math.floor(random.random() * 10)]
    #return OTP
    msg = "Your verification code is "+OTP+". Do not share it with anyone."
    receiver_list='"'+mobile_no+'"'
    send_sms(receiver_list,msg)
    return OTP