# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "club_crm"
app_title = "Club CRM"
app_publisher = "Blue Lynx"
app_description = "CRM for Health Club and Spa"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "admin@bluelynx.qa"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
#app_include_css = ["/assets/club_crm/css/fullcalendar.min.css","/assets/club_crm/css/scheduler.min.css"]
#app_include_css = "/assets/club_crm/css/scheduler.min.css"
#app_include_js = ["/assets/club_crm/js/fullcalendar.min.js","/assets/club_crm/js/scheduler.min.js"]
#app_include_js = "/assets/club_crm/js/scheduler.min.js"
# include js, css files in header of web template
# web_include_css = "/assets/club_crm/css/club_crm.css"
# web_include_js = "/assets/club_crm/js/club_crm.js"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "club_crm.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "club_crm.install.before_install"
# after_install = "club_crm.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "club_crm.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
 	"User": {
    	"after_insert": "club_crm.core.doctype.user.user.create_client_user"
    },
	"Payment Log": {
		"on_submit" : "club_crm.club_crm.doctype.payment_log.payment_log.make_paid"
	}
	# "Memberships": {
	# 	"after_insert": "club_crm.club_crm.doctype.client_sessions.client_sessions.create_sessions"
	# }
    # "Client": {
    #              "after_insert": "club_crm.club_crm.doctype.client.client.create_customer_client"
    #              }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
 	"daily": [
 		"club_crm.club_crm.doctype.spa_appointment.spa_appointment.update_appointment_status",
        "club_crm.club_crm.doctype.client.client.auto_checkout",
		"club_crm.club_crm.doctype.memberships.memberships.update_membership_status"
 	],
	"hourly": [
		"club_crm.club_crm.doctype.spa_appointment.spa_appointment.update_appointment_status"
	]
# 	"weekly": [
# 		"club_crm.tasks.weekly"
# 	]
# 	"monthly": [
# 		"club_crm.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "club_crm.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "club_crm.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "club_crm.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]
fixtures = [
    "Workflow",
    {"dt": "Role", "filters": [["disabled", "=", 0]]},
	"Workflow State",
	"Workflow Action Master"
]

email_brand_image = "assets/club_crm/images/katara-club.jpg"

default_mail_footer = """
	<span>
		Sent by
		<a class="text-muted" href="https://katara.club" target="_blank">
			Katara Club
		</a>
	</span>
"""
