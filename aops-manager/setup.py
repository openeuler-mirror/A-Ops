#!/usr/bin/python3
"""
Description: setup up the A-ops manager service.
"""

from setuptools import setup, find_packages


setup(
    name='aops-manager',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'ansible>=2.9.0',
        'PyYAML',
        'marshmallow>=3.13.0',
        'Flask',
        'Flask-RESTful',
        'requests'
        ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/manager.ini']),
        ('/usr/lib/systemd/system', ['aops-manager.service']),
    ],
    scripts=['aops-manager'],
    zip_safe=False
)
