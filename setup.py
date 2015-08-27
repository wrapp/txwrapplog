#!/usr/bin/env python

from setuptools import setup

setup(
    name='pywrapplog',
    version='0.1.0',
    py_modules=['wrapplog'],
    install_requires=[
        'twisted',
    ],
    zip_safe=False,
)
