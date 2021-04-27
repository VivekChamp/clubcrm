# -*- coding: utf-8 -*-
# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import requests
import json

class PushNotificationCenter(Document):
	def send_notification(self):
		server_key = frappe.db.get_value("Push Notification Settings",None,"server_token")
		
		if self.send_to == "Single Client":
			client = frappe.get_doc("Client", self.client_id)
			device_token = client.fcm_token
			headers = {
				'Content-Type': 'application/json',
				'Authorization': 'key=' + server_key,
			}
			body = {
				'notification': {
					'title': self.title,
					'body': self.message
					},
				'to':
					device_token,
					'priority': 'high',
			}
			response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
			frappe.msgprint(msg='Push Notification sent successfully')
		
		if self.send_to == "All Registered Clients":
			client_list = frappe.get_all('Client', filters={'reg_on_app': 'Yes'}, fields=['name','fcm_token'])
			if client_list:
				for client in client_list:
					# client_ = frappe.get_doc("Client", client.client_id)
					device_token = client.fcm_token
					headers = {
						'Content-Type': 'application/json',
						'Authorization': 'key=' + server_key,
					}
					body = {
						'notification': {
							'title': self.title,
							'body': self.message
							},
						'to':
							device_token,
							'priority': 'high',
					}
					response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
				frappe.msgprint(msg='Push Notification sent successfully')

@frappe.whitelist()
def send_push_notification(client_id,title,message):
	server_key = frappe.db.get_value("Push Notification Settings",None,"server_token")
	client = frappe.get_doc("Client", client_id)
	device_token = client.fcm_token
	headers = {
		'Content-Type': 'application/json',
		'Authorization': 'key=' + server_key,
	}
	body = {
		'notification': {
			'title': title,
			'body': message
		},
		'to':
			device_token,
		'priority': 'high',
	}
	response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
	frappe.msgprint(msg='Push Notification sent successfully')

 