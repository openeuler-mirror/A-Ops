# coding: utf-8

from setuptools import setup, find_packages

NAME = "aops_check"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    'marshmallow>=3.13.0',
    'Flask',
    'Flask-RESTful',
    'Flask-APScheduler',
    'numpy',
    'pandas',
    'prometheus_api_client',
    'setuptools',
    'requests',
    'SQLAlchemy',
    'PyMySQL',
    'scipy',
    'statsmodels'
]

setup(
    name=NAME,
    version=VERSION,
    description="aops-check",
    install_requires=REQUIRES,
    packages=find_packages(),
    data_files=[
        ('/etc/aops', ['conf/check.ini']),
        ('/usr/lib/systemd/system', ['aops-check.service'])
    ],
    entry_points={
        'console_scripts': ['aops-check=aops_check.manage:main']
    },
    zip_safe=False
)
