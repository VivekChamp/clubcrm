from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'document_id',
		'transactions': [
			{
				'label': _(''),
				'items': ['Rating']
			}
		]	
	}