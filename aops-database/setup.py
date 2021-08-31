#!/usr/bin/python3
"""
Description: setup up the A-ops database center.
"""
from setuptools import setup, find_packages

setup(
    name='aops-database',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'SQLAlchemy',
        'elasticsearch>=7',
        'prometheus_api_client',
        'PyMySQL',
        'Werkzeug',
        'urllib3',
        'Flask',
        'Flask-RESTful',
        'requests',
        'PyYAML'
        ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/database.ini']),
        ('/usr/lib/systemd/system', ['aops-database.service']),
    ],
    scripts=['aops-basedatabase', 'aops-database'],
    zip_safe=False
)


