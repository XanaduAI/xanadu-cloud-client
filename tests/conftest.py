"""
This module contains shared pytest fixtures.
"""
from tempfile import NamedTemporaryFile
from typing import Iterator

import pytest

import xcc


@pytest.fixture
def connection() -> xcc.Connection:
    """Returns a mock connection."""
    return xcc.Connection(refresh_token="j.w.t", host="cloud.xanadu.ai", port=443, tls=True)


@pytest.fixture(autouse=True)
def settings(monkeypatch) -> Iterator[xcc.Settings]:
    """Returns a :class:`xcc.Settings` instance configured to use a mock .env file."""
    with NamedTemporaryFile("w") as env_file:
        monkeypatch.setattr("xcc.Settings.Config.env_file", env_file.name)

        settings_ = xcc.Settings(REFRESH_TOKEN="j.w.t", HOST="example.com", PORT=80, TLS=False)
        # Saving ensures that new Settings instances are loaded with the same values.
        settings_.save()

        yield settings_
