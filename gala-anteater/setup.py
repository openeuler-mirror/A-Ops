# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="gala_anteater",
    version="0.0.1",
    author="Zhenxing Li",
    author_email="lizhenxing11@huawei.com",
    description="Times Series Anomaly Detection Platform on Operating System",
    url="https://gitee.com/openeuler/A-Ops/tree/master/gala-anteater",
    keywords=["Anomaly Detection", "Time Series Analysis", "Operating System"],
    packages=find_packages(where="."),
    package_data={
        "anteater":
            [
                # configs
                "configuration/log.settings.ini",
                "configuration/model.settings.ini",
                "configuration/service.settings.ini",

                # models
                "file/normalization.pkl",
                "file/rf_model.pkl",
                "file/vae_model.torch",
                "file/vae_parameters.json",

                # features
                "model/observe/metrics.csv",
            ],
    },
	data_files=[
        ('/usr/lib/systemd/system/', ['service/gala-anteater.service']),
    ],
    install_requires=[
        "APScheduler==3.9.1",
        "kafka-python>=2.0.2",
        "joblib==0.14.1",
        "numpy==1.21.6",
        "pandas==1.0.1",
        "requests==2.28.1",
        "scikit_learn==0.24.2",
        "torch==1.11.0"
    ],
    entry_points={
        "console_scripts": [
            "gala-anteater = anteater.main:main",
        ]
    }
)
