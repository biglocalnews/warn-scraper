#!/usr/bin/env python
"""Configure the package for distribution."""
import distutils.cmd
import os
from importlib import import_module
from pathlib import Path

import jinja2
import us
from setuptools import setup

import warn

# from setuptools import find_packages, setup


def read(file_name):
    """Read the provided file."""
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, file_name)
    with open(file_path) as f:
        return f.read()


def version_scheme(version):
    """
    Version scheme hack for setuptools_scm.

    Appears to be necessary to due to the bug documented here: https://github.com/pypa/setuptools_scm/issues/342

    If that issue is resolved, this method can be removed.
    """
    import time

    from setuptools_scm.version import guess_next_version

    if version.exact:
        return version.format_with("{tag}")
    else:
        _super_value = version.format_next_version(guess_next_version)
        now = int(time.time())
        return _super_value + str(now)


def local_version(version):
    """
    Local version scheme hack for setuptools_scm.

    Appears to be necessary to due to the bug documented here: https://github.com/pypa/setuptools_scm/issues/342

    If that issue is resolved, this method can be removed.
    """
    return ""


class TallyCommand(distutils.cmd.Command):
    """Tally scrapers and update sources dashboard in the docs."""

    description = "Tally scrapers and update sources dashboard in the docs"
    user_options: list = []

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Finalize values."""
        pass

    def run(self):
        """Run command."""
        print("Tallying sources")

        this_dir = Path(__file__).parent
        loader = jinja2.FileSystemLoader(searchpath=this_dir / "docs" / "_templates/")
        env = jinja2.Environment(loader=loader)

        scraper_list = warn.utils.get_all_scrapers()
        print(f"{len(scraper_list)} scrapers found")

        docs_dir = this_dir / "docs" / "scrapers"
        has_docs = [f.stem for f in docs_dir.glob("*.md") if f.stem in scraper_list]
        print(f"{len(has_docs)} scrapers have docs")

        haves, have_nots = [], []
        target_list = us.states.STATES_AND_TERRITORIES + [us.states.DC]
        for t in target_list:
            state = t.__dict__
            abbr = state["abbr"].lower()
            if abbr in scraper_list:
                state["has_docs"] = abbr in has_docs
                module = import_module(f"warn.scrapers.{abbr}")
                state["authors"] = sorted(module.__authors__)
                state["tags"] = sorted(module.__tags__)
                state["source"] = module.__source__
                haves.append(state)
            else:
                state["has_docs"] = False
                state["authors"] = None
                state["tags"] = None
                state["source"] = None
                have_nots.append(state)
        print(f"{len(haves)} states and territories have a scraper")
        print(f"{len(have_nots)} states and territories do not have a scraper")

        context = {
            "haves": haves,
            "have_nots": have_nots,
            "targets": target_list,
        }
        template = env.get_template("sources.md.tmpl")
        md = template.render(**context)

        with open(this_dir / "docs" / "sources.md", "w") as fh:
            fh.write(md)


setup(
    cmdclass={
        "tallysources": TallyCommand,
    },
)
