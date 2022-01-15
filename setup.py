#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Configure the package for distribution."""
import os
from setuptools import setup, find_packages


def read(file_name):
    """Read the provided file."""
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, file_name)
    with open(file_path) as f:
        return f.read()


requirements = [
    "bs4",
    "html5lib",
    "pandas",
    "pdfplumber",
    "requests",
    "openpyxl",
    "tenacity",
    "xlrd",
    # Install non-PyPI libraries
    "bln-etl @ git+https://github.com/biglocalnews/bln-etl.git",
]

test_requirements = [
    "pytest",
    "pytest-vcr",
]

setup(
    name="warn-scraper",
    version="0.1.0",
    description="Command-line interface for downloading WARN Act notices of qualified plant closings and mass layoffs from state government websites",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Big Local News",
    url="https://github.com/biglocalnews/WARN",
    packages=find_packages(),
    include_package_data=True,
    entry_points="""
        [console_scripts]
        warn-scraper=warn.cli:main
    """,
    install_requires=requirements,
    license="Apache 2.0 license",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="tests",
    setup_requires=["pytest-runner"],
    tests_require=test_requirements,
    project_urls={
        "Documentation": "https://warn-scraper.readthedocs.io",
        "Maintainer": "https://github.com/biglocalnews",
        "Source": "https://github.com/biglocalnews/WARN",
        "Tracker": "https://github.com/biglocalnews/WARN/issues",
    },
)
