from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'client_id',
		'transactions': [
			{
				'label': _(''),
				'items': ['Check In', 'Client Sessions', 'Spa Appointment','Fitness Training Appointment', 'Group Class Attendees']
			},
			{
				'label': _(''),
 				'items': ['Memberships','Member Benefits','Memberships Application']
			},
            {
				'label': _(''),
				'items': ['Rating','Valet Parking','Online Order','Food Order Entry']
			}
		]	
	}