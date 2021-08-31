# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.connection` module.
"""

from requests.models import HTTPError
import pytest
import responses
from requests.models import HTTPError

import xcc


class TestConnection:
    """Tests the :class:`xcc.Connection` class."""

    def test_access_token(self, connection):
        """Tests that the correct access token is returned for a connection."""
        assert connection.access_token is None

    def test_refresh_token(self, connection):
        """Tests that the correct refresh token is returned for a connection."""
        assert connection.refresh_token == "j.w.t"

    def test_tls(self, connection):
        """Tests that the correct TLS setting is returned for a connection."""
        assert connection.tls is True

    def test_scheme(self):
        """Tests that the correct scheme is returned for a connection."""
        assert xcc.Connection(key="j.w.t", tls=False).scheme == "http"
        assert xcc.Connection(key="j.w.t", tls=True).scheme == "https"

    def test_host(self, connection):
        """Tests that the correct host is returned for a connection."""
        assert connection.host == "cloud.xanadu.ai"

    def test_port(self, connection):
        """Tests that the correct port is returned for a connection."""
        assert connection.port == 443

    def test_api_version(self, connection):
        """Tests that the correct API version is returned for a connection."""
        assert connection.api_version == "0.4.0"

    def test_user_agent(self, connection):
        """Tests that the correct user agent is returned for a connection."""
        assert connection.user_agent == "XanaduCloudClient/0.1.0-dev"

    def test_headers(self, connection):
        """Tests that the correct headers are returned for a connection."""
        assert connection.headers == {
            "Accept-Version": "0.4.0",
            "Authorization": "Bearer None",
            "User-Agent": "XanaduCloudClient/0.1.0-dev",
        }

    def test_repr(self, connection):
        """Tests that the printable representation of a connection is correct."""
        assert repr(connection) == "<Connection: key=j.w.t, url=https://cloud.xanadu.ai:443/>"

    def test_url(self, connection):
        """Tests that the correct URL is derived for a connection path."""
        assert connection.url() == "https://cloud.xanadu.ai:443/"
        assert connection.url("/") == "https://cloud.xanadu.ai:443/"
        assert connection.url("/path/to/thing") == "https://cloud.xanadu.ai:443/path/to/thing"

    @responses.activate
    def test_ping_success(self, connection):
        """Tests that a ping succeeds when a connection is configured correctly."""
        responses.add(responses.GET, connection.url("healthz"), status=200)
        response = connection.ping()
        assert response.status_code == 200

    @responses.activate
    def test_ping_failure(self, connection):
        """Tests that a ping fails when a connection is configured incorrectly."""
        responses.add(responses.GET, connection.url("healthz"), status=400)
        with pytest.raises(HTTPError, match=r"400 Client Error: Bad Request"):
            connection.ping()

    @responses.activate
    def test_request_with_fresh_access_token(self, connection):
        """Tests that the correct response is returned for a connection with an
        access token that has not yet expired."""
        responses.add(responses.GET, connection.url("healthz"), status=200)
        assert connection.request("GET", "/healthz").status_code == 200
        assert len(responses.calls) == 1

    @responses.activate
    def test_request_with_expired_access_token(self, connection):
        """Tests that the correct response is returned for a connection with an
        expired access token."""
        responses.add(responses.GET, connection.url("healthz"), status=401)
        responses.add(responses.GET, connection.url("healthz"), status=200)
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=200,
            body="{}",
        )

        assert connection.request("GET", "/healthz").status_code == 200
        assert len(responses.calls) == 3

    @responses.activate
    def test_update_access_token_success(self, connection):
        """Tests that the access token of a connection can be updated."""
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=200,
            body='{"access_token": "mock.access.token"}',
        )

        connection.update_access_token()

        assert connection.access_token == "mock.access.token"

    @responses.activate
    def test_update_access_token_failure(self, connection):
        """Tests that a XanaduCloudConnectionError is raised when the access
        token of a connection cannot be updated.
        """
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=400,
        )

        with pytest.raises(HTTPError, match=r"400 Client Error: Bad Request"):
            connection.update_access_token()
