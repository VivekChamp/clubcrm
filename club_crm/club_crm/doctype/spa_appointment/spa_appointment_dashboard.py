from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'document_id',
		'non_standard_fieldnames': {
			'Check In': 'spa_booking',
			'Spa Progress Notes': 'appointment_id'
		},
		'transactions': [
			{
				'label': _(''),
				'items': ['Check In', 'Spa Progress Notes', 'Rating']
			}
		]	
	}