
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime, timedelta, date, time
import requests
import json
import datetime
import calendar

@frappe.whitelist()
def add_month(st_date, month):
    # advance year and month by one month
    if type(st_date) == str:
        start_date = datetime.datetime.strptime(st_date, "%Y-%m-%d").date()
    else:
        start_date = st_date

    new_year = start_date.year
    new_month = start_date.month + int(month)
    # note: in datetime.date, months go from 1 to 12
    if new_month > 12:
        new_year += 1
        new_month -= 12

    last_day_of_month = calendar.monthrange(new_year, new_month)[1]
    new_day = min(start_date.day, last_day_of_month)
    expiry_date = start_date.replace(year=new_year, month=new_month, day=new_day)
    return expiry_date