# coding: utf-8

from setuptools import setup, find_packages

NAME = "spider"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion", "requests", "pyyaml", "pyarango"]

setup(
    name=NAME,
    version=VERSION,
    description="Topo Graph Engine Service",
    author_email="zhengxian@huawei.com",
    url="",
    keywords=["Swagger", "Topo Graph Engine Service"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    data_files=[('/etc/spider/', ['config/gala-spider.yaml', 'config/observe.yaml'])],
    include_package_data=True,
    entry_points={
        'console_scripts': ['spider-server=spider.__main__:main',
                            'spider-storage=spider.storage_daemon:main']
    },
    long_description="""\
    Topo Graph Engine Service
    """
)

