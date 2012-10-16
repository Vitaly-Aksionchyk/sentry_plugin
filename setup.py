#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'sentry>=5.0.14',
]

setup(
    name='sentry-ecom',
    version='0.1',
    packages=find_packages(),
    install_requires=install_requires,

    entry_points={
       'sentry.plugins': [
            'ecom = sentry_ecom.plugin:EcomPlugin',
            'profile = sentry_ecom.plugin:ProfileEmailTag',
            'request_method = sentry_ecom.plugin:RequestMethod',
            'econ_func = sentry_ecom.plugin:EcomTaggedFuncs',
        ],
    },
)