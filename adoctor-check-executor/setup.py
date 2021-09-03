#!/usr/bin/python3
"""
Description: setup up the A-doctor check executor service
"""

from setuptools import setup, find_packages

setup(
    name='adocter-check-executor',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'PyYAML',
        'marshmallow>=3.13.0',
        'requests',
        'ply>=3.11',
        'kafka-python>=2.0.2'
    ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/check_executor.ini', 'conf/check_rule_plugin.yml']),
        ('/usr/lib/systemd/system', ['adoctor-check-executor.service']),
    ],
    scripts=['adoctor-check-executor'],
    zip_safe=False
)
