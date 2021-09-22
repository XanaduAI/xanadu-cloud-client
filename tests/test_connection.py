# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.connection` module.
"""

import json

import pytest
import requests
import responses
from requests.exceptions import HTTPError, RequestException

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
        connection._headers["Accept-Version"] = "1.2.3"  # pylint: disable=protected-access
        assert connection.api_version == "1.2.3"

    def test_user_agent(self, connection):
        """Tests that the correct user agent is returned for a connection."""
        assert connection.user_agent == f"XCC/{xcc.__version__} (API)"
        connection._headers["User-Agent"] = "Bond/1.2.3"  # pylint: disable=protected-access
        assert connection.user_agent == "Bond/1.2.3"

    def test_headers(self, connection):
        """Tests that the correct headers are returned for a connection."""
        connection._headers["Accept-Language"] = "en-CA"  # pylint: disable=protected-access
        assert connection.headers == {
            "Accept-Language": "en-CA",
            "Accept-Version": "0.4.0",
            "Authorization": "Bearer None",
            "User-Agent": f"XCC/{xcc.__version__} (API)",
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
    def test_request_success_with_fresh_access_token(self, connection):
        """Tests that the correct response is returned for a connection with an
        access token that has not yet expired."""
        responses.add(responses.GET, connection.url("healthz"), status=200)
        assert connection.request("GET", "/healthz").status_code == 200
        assert len(responses.calls) == 1

    @responses.activate
    def test_request_success_with_expired_access_token(self, connection):
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
    def test_request_failure_due_to_invalid_json(self, connection):
        """Tests that an HTTPError is raised when the status code of the HTTP
        response to a connection request indicates that an error has occurred
        and the body of the response is invalid JSON.
        """
        responses.add(responses.GET, connection.url("healthz"), status=400)
        with pytest.raises(HTTPError, match=r"400 Client Error: Bad Request"):
            connection.request("GET", "/healthz")

    @responses.activate
    def test_request_failure_due_to_validation_error(self, connection):
        """Tests that an HTTPError is raised when the HTTP response of a
        connection request indicates that a validation error occurred and the
        body of the response contains a non-empty "meta" field.
        """
        body = {"code": "validation-error", "meta": {"_schema": ["Foo", "Bar"], "size": ["Baz"]}}
        responses.add(responses.GET, connection.url("healthz"), status=400, body=json.dumps(body))

        with pytest.raises(HTTPError, match=r"Foo; Bar; Baz"):
            connection.request("GET", "/healthz")

    @responses.activate
    def test_request_failure_due_to_detailed_error(self, connection):
        """Tests that an HTTPError is raised when the status code of the HTTP
        response to a connection request indicates that an error occurred and
        the body of the response contains a "detail" field.
        """
        body = {"code": "invalid-request", "detail": "The request body is empty."}
        responses.add(responses.GET, connection.url("healthz"), status=400, body=json.dumps(body))

        with pytest.raises(HTTPError, match=r"The request body is empty"):
            connection.request("GET", "/healthz")

    @responses.activate
    def test_request_failure_due_to_status_code(self, connection):
        """Tests that an HTTPError is raised when the status code of the HTTP
        response to a connection request indicates that an error occurred but
        but no other details about the error are provided.
        """
        responses.add(responses.GET, connection.url("healthz"), status=418, body="{}")
        with pytest.raises(HTTPError, match=r"418 Client Error: I'm a Teapot"):
            connection.request("GET", "/healthz")

    def test_request_failure_due_to_timeout(self, monkeypatch, connection):
        """Tests that a RequestException is raised when a connection request times out."""

        def mock_request(*args, **kwargs):
            raise requests.exceptions.Timeout()

        monkeypatch.setattr("xcc.connection.requests.request", mock_request)

        match = r"GET request to 'https://cloud.xanadu.ai:443/healthz' timed out"
        with pytest.raises(RequestException, match=match):
            connection.request("GET", "/healthz")

    @responses.activate
    def test_request_failure_due_to_hostname_resolution(self, monkeypatch, connection):
        """Tests that a RequestException is raised when the hostname associated
        with a connection request cannot be resolved.
        """

        def mock_request(*args, **kwargs):
            raise requests.exceptions.ConnectionError("Name or service not known")

        monkeypatch.setattr("xcc.connection.requests.request", mock_request)

        match = (
            r"Failed to connect to 'https://cloud.xanadu.ai:443/healthz': "
            r"unknown hostname 'cloud.xanadu.ai'"
        )
        with pytest.raises(RequestException, match=match):
            connection.request("GET", "/healthz")

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
    def test_update_access_token_success_with_invalid_json(self, connection):
        """Tests that a ValueError is raised when the HTTP response to an access
        token request has a 200 status code but the body of the response contains
        invalid JSON.
        """
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=200,
        )

        match = r"Xanadu Cloud returned an invalid access token response\."
        with pytest.raises(ValueError, match=match):
            connection.update_access_token()

    @responses.activate
    def test_update_access_token_failure_due_to_invalid_json(self, connection):
        """Tests that an HTTPError is raised when the status code of an HTTP
        response to an access token request indicates that an error occurred and
        the body of the response contains invalid JSON.
        """
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=400,
        )

        with pytest.raises(HTTPError, match=r"400 Client Error: Bad Request"):
            connection.update_access_token()

    @responses.activate
    def test_update_access_token_failure_due_to_invalid_refresh_token(self, connection):
        """Tests that an HTTPError is raised when the HTTP response to an access
        token request indicates that the refresh token (API key) is invalid.
        """
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=400,
            body='{"error": "invalid_grant"}',
        )

        with pytest.raises(HTTPError, match=r"Xanadu Cloud API key is invalid"):
            connection.update_access_token()

    @responses.activate
    def test_update_access_token_failure_due_to_status_code(self, connection):
        """Tests that an HTTPError is raised when the HTTP response to an access
        token request contains valid JSON but its status code indicates that an
        error occurred.
        """
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=418,
            body="{}",
        )

        with pytest.raises(HTTPError, match=r"418 Client Error: I'm a Teapot"):
            connection.update_access_token()
