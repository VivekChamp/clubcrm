# Copyright (c) 2021, Blue Lynx and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from club_crm.club_crm.doctype.client_sessions.client_sessions import create_additional_benefit_sessions

class AdditionalBenefits(Document):
	pass

@frappe.whitelist()
def activate_additional_benefits(doc_id):
	doc = frappe.get_doc('Additional Benefits', doc_id)
	mem = frappe.get_doc('Memberships', doc.membership)

	if doc.additional_benefits_item:
		for row in doc.additional_benefits_item:

			create_additional_benefit_sessions(doc.client_id, mem.start_date, row.service_type, row.service_name, row.no_of_sessions, row.validity, doc.membership)
	
	frappe.db.set_value('Additional Benefits', doc_id, 'benefit_activated', 1)
	
	frappe.msgprint(msg = "Additonal Benefits activated.", title="Success")
