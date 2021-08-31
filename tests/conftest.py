import pytest

import xcc


@pytest.fixture
def connection() -> xcc.Connection:
    """Returns a mock connection."""
    return xcc.Connection(key="j.w.t", host="cloud.xanadu.ai", port=443, tls=True)
