#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()

with open('requirements-minimal.txt') as requirements_file:
    requirements = requirements_file.readlines()

with open('requirements-dev-minimal.txt') as requirements_dev_file:
    requirements_dev = requirements_dev_file.readlines()

setup(
    name='swagger_code_generator',
    version='0.0.0',
    description="Short Description.",
    long_description=readme + '\n\n' + changelog,
    author="Samuele Maci",
    author_email='macisamuele@gmail.com',
    url='https://github.com/macisamuele/swagger_code_generator',
    packages=[
        'swagger_code_generator',
    ],
    package_dir={'swagger_code_generator': 'swagger_code_generator'},
    include_package_data=True,
    install_requires=requirements,
    tests_require=requirements_dev,
    license="BSD license",
    zip_safe=False,
    keywords='swagger_code_generator',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
