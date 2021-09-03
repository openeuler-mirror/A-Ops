#!/usr/bin/python3
"""
Description: setup.
"""
from setuptools import setup, find_packages


setup(
    name='adoctor-diag-scheduler',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-RESTful',
        'requests',
        'kafka-python>=2.0.2',
        'uWSGI'
    ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/diag_scheduler.ini']),
        ('/usr/lib/systemd/system', ['adoctor-diag-scheduler.service']),
    ],
    scripts=['diag-scheduler-manager'],
    zip_safe=False
)
