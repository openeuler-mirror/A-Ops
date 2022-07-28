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
DESC = "OS Topological Graph Storage Service and Cause Inference Service"
LONG_DESC = """
OS Topological Graph Storage Service and Cause Inference Service
"""

INSTALL_REQUIRES = [
    "requests",
    "pyyaml",
    "pyarango>=2.0.1",
    "kafka-python>=2.0.2",
]

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    author_email="hexiujun1@huawei.com",
    url="https://gitee.com/openeuler/A-Ops/tree/master/gala-spider",
    keywords=["OS Topological Graph Storage", "Cause Inference"],
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(exclude=('tests',)),
    data_files=[
        ('/etc/gala-spider/', ['config/gala-spider.yaml', 'config/topo-relation.yaml', 'config/ext-observe-meta.yaml']),
        ('/etc/gala-inference/', ['config/gala-inference.yaml', 'config/ext-observe-meta.yaml']),
        ('/usr/lib/systemd/system/', ['service/gala-spider.service', 'service/gala-inference.service']),
    ],
    entry_points={
        'console_scripts': [
            'spider-storage=spider.storage_daemon:main',
            'gala-inference=cause_inference.__main__:main',
        ]
    },
    long_description=LONG_DESC,
)

