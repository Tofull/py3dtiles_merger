#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import py3dtiles_merger

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='py3dtiles_merger',
    version=py3dtiles_merger.__version__,
    description="Merge independant 3dtiles tileset.json generated with py3dtiles into one.",
    long_description=long_description,
    author="Loïc Messal",
    author_email='Tofull@users.noreply.github.com',
    url='https://github.com/tofull/py3dtiles_merger',
    packages=find_packages(include=['py3dtiles_merger']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: French',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': ['py3dtiles_merger=py3dtiles_merger.command_line:command_line'],
    }
)