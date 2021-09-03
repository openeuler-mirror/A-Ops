#!/usr/bin/python3
"""
Description: setup.
"""
from setuptools import setup, find_packages


setup(
    name='adoctor-diag-executor',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'kafka-python>=2.0.2'
    ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/diag_executor.ini']),
        ('/usr/lib/systemd/system', ['adoctor-diag-executor.service']),
    ],
    scripts=['adoctor-diag-executor'],
    zip_safe=False
)
