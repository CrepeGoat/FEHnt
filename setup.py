#!/usr/bin/env python

from setuptools import setup

setup(
    # Metadata
    name='Fehnt',
    version='0.1',
    description='FEH gotcha outcome probability calculator',
    author='CrepeGoat',
    # Contents
    packages=['fehnt'],
    # Dependencies
    install_requires=['pandas', 'sortedcontainers', 'static_frame==0.3.1'],
    #tests_requires=['pytest'],
)
