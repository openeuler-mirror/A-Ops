#!/usr/bin/python3
"""
Description: setup up the A-ops utils module.
"""
from setuptools import setup, find_packages

setup(
    name='aops-utils',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'concurrent-log-handler',
        'xmltodict',
        'PyYAML',
        'marshmallow>=3.13.0',
        'xlrd',
        'requests',
    ],
    author='cmd-lsw-yyy-zyc',
    data_files=[
        ('/etc/aops', ['conf/system.ini'])
    ],
    scripts=['aops-utils'],
    zip_safe=False
)


