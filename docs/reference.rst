#########
Reference
#########

Documentation for a selection of our system’s common internal tools

.. contents:: Table of contents
    :depth: 1
    :local:

Makefile
########

A number of custom commands are available to developers via `make <https://www.gnu.org/software/make/>`_. They offer options for quickly running tests, working with the docs and executing scrapers.

.. code-block:: bash

    build-release        builds source and wheel package
    check-release        check release for potential errors
    coverage             check code coverage
    format               automatically format Python code with black
    help                 Show this help. Example: make help
    lint                 run the linter
    mypy                 run mypy type checks
    run                  run a scraper. example: `make run scraper=IA`
    serve-docs           start the documentation test server
    tally-sources        update sources dashboard in the docs
    test-docs            build the docs as html
    test                 run all tests

For example, you can run this from the root of the project.

.. code-block:: bash

    make run scraper=IA

Caching
#######

The `Cache` class is used to save the raw HTML, PDFs and CSVs files our scrapers collect.

.. automodule:: warn.cache
    :members:

Utilities
#########

The [utils](https://github.com/biglocalnews/warn-scraper/blob/main/warn/utils.py) module contains a variety of variables and functions used by our scrapers.

.. automodule:: warn.utils
    :members:
