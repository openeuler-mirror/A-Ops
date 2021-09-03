#!/usr/bin/python3
"""
Description: setup up the A-doctor check scheduler service
"""

from setuptools import setup, find_packages


setup(
    name='adocter-check-scheduler',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'marshmallow>=3.13.0',
        'Flask',
        'Flask-RESTful',
        'requests',
        'flask_apscheduler>=1.12.2',
        'kafka-python>=2.0.2',
        'uWSGI'
        ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/check_scheduler.ini']),
        ('/usr/lib/systemd/system', ['adoctor-check-scheduler.service']),
    ],
    scripts=['adoctor-check-scheduler'],
    zip_safe=False
)


