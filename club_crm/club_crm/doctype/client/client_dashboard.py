from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'client_id',
		'transactions': [
			{
				'label': _('Appointments'),
				'items': ['Spa Appointment', 'Group Class Attendees', 'Check In', 'Rating']
			},
			{
				'label': _('Membership Details'),
 				'items': ['Memberships', 'Membership Benefits', 'Memberships Application']
			},
            {
				'label': _('Orders'),
				'items': ['Online Order', 'Food Order']
			}
		]	
	}