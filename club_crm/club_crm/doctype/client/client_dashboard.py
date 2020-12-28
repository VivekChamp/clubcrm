from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'client_id',
		'transactions': [
			{
				'label': _('Appointments'),
				'items': ['Spa Appointment','Group Class Attendees','Fitness Training Appointment','Grams Reservation','Club Tour']
			},
			{
				'label': _('Membership'),
 				'items': ['Memberships','Member Benefits','Memberships Application','Fitness Training Session']
			},
            {
				'label': _('Others'),
				'items': ['Check In','Rating','Valet Parking','Online Order','Food Order Entry']
			},
			{
				'label': _('Transactions'),
				'items': ['Wallet Transaction']
			}
		]	
	}