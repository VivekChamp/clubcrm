# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, get_time, flt, now_datetime
from datetime import datetime, timedelta, date, time
from frappe.model.document import Document

class ValetParking(Document):
	def before_insert(self):
		if self.status=="Parked":
			valet = frappe.get_all('Valet Parking', filters={'date':self.date,'vehicle_no':self.vehicle_no}, fields=["*"])
			if valet:
				valet_check = valet[0]
				if valet_check.status=="Parked":
					frappe.throw('This vehicle is already parked')
					return "This vehicle is already parked"
				
@frappe.whitelist()
def release_parked_vehicle():
	vehicle_list = frappe.get_all('Valet Parking', filters={'status': 'Parked'})
	if vehicle_list:
		for vehicles in vehicle_list:
			vehicle = frappe.get_doc('Valet Parking', vehicles.name)
			vehicle.status = 'Delivered'
			vehicle.delivery_time = datetime.now()
			vehicle.save()
			frappe.db.set_value('Valet Parking', vehicle.name, 'docstatus', 1)
			frappe.db.commit()


