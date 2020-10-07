# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in club_crm/__init__.py
from club_crm import __version__ as version

setup(
	name='club_crm',
	version=version,
	description='CRM for Health Club and Spa',
	author='Blue Lynx',
	author_email='admin@bluelynx.qa',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
