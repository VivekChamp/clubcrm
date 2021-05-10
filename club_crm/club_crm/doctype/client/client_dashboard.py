from __future__ import unicode_literals
import frappe
from frappe import _

def get_data():
	return {
		'fieldname': 'client_id',
		# 'non_standard_fieldnames': {
		# 	'Memberships': 'primary_client_id'
		# },

		'transactions': [
			{
				'label': _(''),
				'items': ['Check In', 'Client Sessions', 'Spa Appointment', 'Club Tour']
			},
			{
				'label': _(''),
 				'items': ['Cart','Memberships Application','Fitness Training Appointment']
			},
            {
				'label': _(''),
				'items': ['Valet Parking','Online Order','Food Order Entry']
			}
		]	
	}