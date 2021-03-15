# -*- coding: utf-8 -*-
# Copyright (c) 2020, Blue Lynx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ClubRoom(Document):
	pass

@frappe.whitelist(allow_guest=True)
def display_service_room(spa_service):
	spa_service= frappe.get_doc('Spa Services', spa_service)
	rooms = []
	for room in spa_service.male_rooms:
		rooms.append(room.room)
	return rooms