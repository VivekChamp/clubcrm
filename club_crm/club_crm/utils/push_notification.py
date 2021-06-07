# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import requests
import json

@frappe.whitelist()
def send_push(client_id,title,msg):
	server_key = frappe.db.get_value("Push Notification Settings",None,"server_token")
	client = frappe.get_doc("Client", client_id)
	device_token = client.fcm_token
	header = {
		'Content-Type': 'application/json',
		'Authorization': 'key=' + server_key,
	}
	body = {
		'notification': {
			'title': title,
			'body': msg
		},
		'to': device_token,
		'priority': 'high',
	}
	response = requests.post("https://fcm.googleapis.com/fcm/send",headers = header, data=json.dumps(body))