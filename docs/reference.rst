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

The `utils <https://github.com/biglocalnews/warn-scraper/blob/main/warn/utils.py>`_ module contains a variety of variables and functions used by our scrapers.

.. automodule:: warn.utils
    :members:


Research
########

CRS
---

A 2013 summary by the Congressional Research Service

.. raw:: html

    <iframe
      src="https://embed.documentcloud.org/documents/21403574-crs-report-on-the-warn-act/?embed=1&amp;responsive=1&amp;title=1"
      title="CRS report on the WARN Act (Hosted by DocumentCloud)"
      width="700"
      height="905"
      style="border: 1px solid #aaa; width: 100%; height: 800px; height: calc(100vh - 100px);"
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-popups-to-escape-sandbox"
    ></iframe>

GAO
---

A 2003 audit by the Government Accountability Office

.. raw:: html

    <iframe
      src="https://embed.documentcloud.org/documents/21403760-gao-audit-the-worker-adjustment-and-retraining-notification-act/?embed=1&amp;responsive=1&amp;title=1"
      title="GAO Audit: &quot;THE WORKER ADJUSTMENT AND RETRAINING NOTIFICATION ACT&quot; (Hosted by DocumentCloud)"
      width="700"
      height="905"
      style="border: 1px solid #aaa; width: 100%; height: 800px; height: calc(100vh - 100px);"
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-popups-to-escape-sandbox"
    ></iframe>
