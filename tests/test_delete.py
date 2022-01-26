import pytest

import warn


@pytest.mark.vcr()
def test_delete():
    """Test delete option."""
    runner = warn.Runner()
    runner.scrape("ia")
    runner.delete()
