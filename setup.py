#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


requirements = [
    'bs4',
    'html5lib',
    'pandas',
    'requests',
    'openpyxl',
    # Install non-PyPI libraries
    'bln-etl @ git+https://github.com/biglocalnews/bln-etl.git',
]

test_requirements = [
    'pytest',
    'pytest-vcr',
]

setup(
    name='warn',
    version='0.1.0',
    description="WARN Layoff notice scrapers.",
    long_description="Web scrapers to gather WARN layoff data from state sites and upload to BLN platform.",
    author="Dilcia Mercedes",
    author_email='dilcia19@stanford.edu',
    url='https://github.com/biglocalnews/WARN',
    packages=find_packages(),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        warn-scraper=warn.cli:main
    ''',
    install_requires=requirements,
    license="Apache 2.0 license",
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
