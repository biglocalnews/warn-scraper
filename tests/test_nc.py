import csv
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from warn.scrapers import nc

from .conftest import read_fixture

# The summary list for 2026, as served on Nov. 16, 2026
HTML = read_fixture("nc_2026.html")


def test_parse_table():
    """Parse the saved page into a header and one row per notice."""
    rows = nc.parse_table(HTML)
    assert rows[0] == nc.EXPECTED_HEADERS
    assert len(rows) == 1 + 71
    assert rows[1] == [
        "New Hanover County",
        "202600001",
        "1/7/2026",
        "1/7/2026",
        "3/6/2026",
        "Avelo Airlines, Inc.",
        "Closure",
        "Permanent",
        "82",
        "1740 Airport Blvd.",
        "Wilmington",
    ]
    assert all(len(r) == len(rows[0]) for r in rows)


def test_scrape_writes_csv(tmp_path):
    """Fetch once, cache the raw page and write nc.csv."""
    with patch("warn.utils.get_url") as get_url:
        get_url.return_value = SimpleNamespace(text=HTML)
        data_path = nc.scrape(tmp_path / "exports", tmp_path / "cache")
    assert get_url.call_count == 1
    assert data_path == tmp_path / "exports" / "nc.csv"
    with open(data_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 71
    assert rows[-1]["WARN Notice: WARN Notice Name"] == "Mueller Systems, LLC"
    assert rows[-1]["Number affected at this location"] == "70"
    cached = list((tmp_path / "cache" / "nc").glob("*.html"))
    assert len(cached) == 1


def test_no_table():
    """A page with no notice table is an error, not an empty file."""
    with pytest.raises(ValueError, match="no WARN notice table"):
        nc.parse_table("<html><body><p>Page not found</p></body></html>")


def test_empty_table():
    """A table with a header and no notices is an error."""
    head = "".join(f"<th>{h}</th>" for h in nc.EXPECTED_HEADERS)
    with pytest.raises(ValueError, match="has no rows"):
        nc.parse_table(f"<table><thead><tr>{head}</tr></thead><tbody></tbody></table>")


def test_changed_columns():
    """A renamed column is reported by name."""
    changed = HTML.replace("<th>Effective Date</th>", "<th>Layoff Date</th>")
    assert changed != HTML
    with pytest.raises(ValueError, match="missing expected columns.*Effective Date"):
        nc.parse_table(changed)
