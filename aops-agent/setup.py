# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "aops_agent"
VERSION = "1.0.0"

INSTALL_REQUIRES = [
    "flask",
    "flask-testing",
    "jsonschema",
    "requests",
    "libconf",
    "connexion",
    "swagger-ui-bundle>=0.0.2",
    "concurrent_log_handler",
    "responses"
]

setup(
    name=NAME,
    version=VERSION,
    description="ApplicationTitle",
    author_email="",
    url="",
    keywords=["Swagger", "A-Ops agent"],
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    data_files=[
        ('/etc/aops', ['conf/agent.conf']),
        ('/usr/lib/systemd/system', ['aops-agent.service']),
    ],
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['aops_agent=aops_agent.__main__:main']},
    long_description="""\
    GroupDesc
    """
)
