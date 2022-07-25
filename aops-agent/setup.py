# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "agent"
VERSION = "1.0.0"

REQUIRES = [
    "connexion",
    "swagger-ui-bundle>=0.0.2"
]

setup(
    name=NAME,
    version=VERSION,
    description="ApplicationTitle",
    author_email="",
    url="",
    keywords=["Swagger", "ApplicationTitle"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['agent=agent.__main__:main']},
    long_description="""\
    GroupDesc
    """
)
