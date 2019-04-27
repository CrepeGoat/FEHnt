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
    install_requires='pandas static_frame sortedcontainers'.split(),
    #tests_requires=['pytest'],
)
