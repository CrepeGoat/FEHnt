#!/usr/bin/env python

from setuptools import setup

setup(
    # Metadata
    name='Fehnt',
    version='0.1',
    description='FEH gacha outcome probability calculator',
    author='CrepeGoat',
    # Contents
    packages=['fehnt'],
    # Dependencies
    install_requires=['sortedcontainers', 'numpy', 'frozendict'],
    #tests_requires=['pytest'],
)
