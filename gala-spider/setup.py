# coding: utf-8
from setuptools import setup, find_packages

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

NAME = "gala-spider"
VERSION = "1.0.0"
DESC = "OS Topological Graph Storage Service"
LONG_DESC = """
OS Topological Graph Storage Service
"""

INSTALL_REQUIRES = [
    "requests",
    "pyyaml",
    "pyarango==2.0.1",
    "kafka-python==2.0.2",
]

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    author_email="hexiujun1@huawei.com",
    url="https://gitee.com/openeuler/A-Ops/tree/master/gala-spider",
    keywords=["OS Topological Graph Storage Service"],
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(exclude=('tests', 'cause_inference')),
    data_files=[
        ('/etc/gala-spider/', ['config/gala-spider.yaml', 'config/topo-relation.yaml', 'config/ext-observe-meta.yaml']),
    ],
    entry_points={
        'console_scripts': [
            'spider-storage=spider.storage_daemon:main',
        ]
    },
    long_description=LONG_DESC,
)

