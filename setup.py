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


def branch_scheme(version):
    """
    Local version scheme for setuptools_scm that adds the branch name for better reproducibility.

    This appears to be necessary to due to the documented at https://github.com/pypa/setuptools_scm/issues/342

    If that issue is resolved, this method can be removed.
    """
    if version.exact or version.node is None:
        return version.format_choice("", "+d{time:{time_format}}", time_format="%Y%m%d")
    else:
        if version.branch == "main":
            return version.format_choice("+{node}", "+{node}.dirty")
        else:
            return version.format_choice("+{node}.{branch}", "+{node}.{branch}.dirty")


setup(
    name="warn-scraper",
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
    install_requires=[
        "bs4",
        "html5lib",
        "pandas",
        "pdfplumber",
        "requests",
        "openpyxl",
        "tenacity",
        "xlrd",
        # TODO: Release this package on PyPI so we can require it like everything else.
        # "bln-etl @ git+ssh://git@github.com/biglocalnews/bln-etl.git",
    ],
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
        "Programming Language :: Python :: 3.10",
    ],
    test_suite="tests",
    tests_require=[
        "pytest",
        "pytest-vcr",
    ],
    setup_requires=["pytest-runner", "setuptools_scm"],
    use_scm_version={"local_scheme": branch_scheme},
    project_urls={
        "Documentation": "https://warn-scraper.readthedocs.io",
        "Maintainer": "https://github.com/biglocalnews",
        "Source": "https://github.com/biglocalnews/WARN",
        "Tracker": "https://github.com/biglocalnews/WARN/issues",
    },
)
