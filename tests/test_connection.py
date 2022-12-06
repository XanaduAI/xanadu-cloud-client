# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.connection` module.
"""

import json

import pytest
import requests
import responses
from requests.exceptions import HTTPError, RequestException
from responses import matchers

import xcc


class TestConnection:
    """Tests the :class:`xcc.Connection` class."""

    @pytest.mark.usefixtures("settings")
    def test_load_with_implicit_settings(self):
        """Tests that a connection can be loaded with an implicit settings configuration."""
        connection = xcc.Connection.load()
        assert connection.refresh_token == "j.w.t"
        assert connection.access_token is None
        assert connection.host == "example.com"
        assert connection.port == 80
        assert connection.tls is False

    @pytest.mark.usefixtures("settings")
    def test_load_with_explicit_settings(self):
        """Tests that a connection can be loaded with an explicit settings configuration."""
        settings = xcc.Settings(
            REFRESH_TOKEN=None,
            ACCESS_TOKEN="j.w.t",
            HOST="not.example.com",
            PORT=443,
            TLS=True,
        )

        connection = xcc.Connection.load(settings)
        assert connection.refresh_token is None
        assert connection.access_token == "j.w.t"
        assert connection.host == "not.example.com"
        assert connection.port == 443
        assert connection.tls is True

    @pytest.mark.usefixtures("settings")
    def test_load_with_keyword_arguments(self):
        """Tests that a connection can be loaded with new or overridden keyword arguments."""
        connection = xcc.Connection.load(host="not.example.com", headers={"User-Agent": "Bond"})
        assert connection.refresh_token == "j.w.t"
        assert connection.access_token is None
        assert connection.host == "not.example.com"
        assert connection.port == 80
        assert connection.tls is False
        assert connection.user_agent == "Bond"

    def test_missing_access_token_and_refresh_token(self):
        """Tests that a ValueError is raised when a connection is created
        without a refresh token or an access token.
        """
        match = (
            r"A refresh token \(e\.g\.\, Xanadu Cloud API key\) or an access "
            r"token must be provided to connect to the Xanadu Cloud"
        )
        with pytest.raises(ValueError, match=match):
            xcc.Connection()

    def test_access_token(self):
        """Tests that the correct access token is returned for a connection."""
        assert xcc.Connection(refresh_token="j.w.t").access_token is None
        assert xcc.Connection(access_token="j.w.t").access_token == "j.w.t"

    def test_refresh_token(self):
        """Tests that the correct refresh token is returned for a connection."""
        assert xcc.Connection(refresh_token="j.w.t").refresh_token == "j.w.t"
        assert xcc.Connection(access_token="j.w.t").refresh_token is None

    def test_tls(self, connection):
        """Tests that the correct TLS setting is returned for a connection."""
        assert connection.tls is True

    def test_scheme(self):
        """Tests that the correct scheme is returned for a connection."""
        assert xcc.Connection(refresh_token="j.w.t", tls=False).scheme == "http"
        assert xcc.Connection(refresh_token="j.w.t", tls=True).scheme == "https"

    def test_host(self, connection):
        """Tests that the correct host is returned for a connection."""
        assert connection.host == "test.xanadu.ai"

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
        assert repr(connection) == (
            "<Connection: refresh_token=j.w.t, access_token=None, url=https://test.xanadu.ai:443/>"
        )

    def test_url(self, connection):
        """Tests that the correct URL is derived for a connection path."""
        assert connection.url() == "https://test.xanadu.ai:443/"
        assert connection.url("/") == "https://test.xanadu.ai:443/"
        assert connection.url("/path/to/thing") == "https://test.xanadu.ai:443/path/to/thing"

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

    @pytest.mark.parametrize(
        "meta, match",
        [
            (
                {
                    "_schema": ["Foo", "Bar"],
                    "size": ["Baz"],
                },
                r"Foo; Bar; Baz",
            ),
            (
                {
                    "head": {"0": ["Foo", "Bar"]},
                    "tail": {"0": ["Baz"], "1": ["Bud"]},
                },
                r"Foo; Bar; Baz; Bud",
            ),
            (
                {
                    "List": ["Foo"],
                    "Dict": {"0": ["Bar"]},
                },
                r"Foo; Bar",
            ),
        ],
    )
    @responses.activate
    def test_request_failure_due_to_validation_error(self, connection, meta, match):
        """Tests that an HTTPError is raised when the HTTP response of a
        connection request indicates that a validation error occurred and the
        body of the response contains a non-empty "meta" field.
        """
        body = {"code": "validation-error", "meta": meta}
        responses.add(responses.GET, connection.url("healthz"), status=400, body=json.dumps(body))

        with pytest.raises(HTTPError, match=match):
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
        no "detail" field is included in the JSON body of the response.
        """
        responses.add(responses.GET, connection.url("healthz"), status=403, body="{}")
        with pytest.raises(HTTPError, match=r"403 Client Error: Forbidden"):
            connection.request("GET", "/healthz")

    @responses.activate
    def test_request_failure_due_to_status_code_while_streaming(self, connection):
        """Tests that an HTTPError is raised when the status code of the HTTP
        response to a connection request where ``stream=True`` indicates that
        an error has occurred.
        """
        responses.add(responses.GET, connection.url("healthz"), status=403, body="{}")
        with pytest.raises(HTTPError, match=r"403 Client Error: Forbidden"):
            connection.request("GET", "/healthz", stream=True)

    def test_request_failure_due_to_timeout(self, monkeypatch, connection):
        """Tests that a RequestException is raised when a connection request times out."""

        def mock_request(*args, **kwargs):
            raise requests.exceptions.Timeout()

        monkeypatch.setattr("xcc.connection.requests.request", mock_request)

        match = r"GET request to 'https://test.xanadu.ai:443/healthz' timed out"
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

        with pytest.raises(RequestException, match=r"Failed to resolve hostname 'test.xanadu.ai'"):
            connection.request("GET", "/healthz")

    @responses.activate
    def test_request_headers(self, connection):
        """Tests that the correct headers are passed when the headers argument is not provided."""

        responses.add(
            url=connection.url("path"),
            method="POST",
            status=200,
            match=(matchers.header_matcher(connection.headers),),
        )

        connection.request(method="POST", path="path")

    @responses.activate
    @pytest.mark.parametrize("extra_headers", [{"X-Test": "data"}, {}])
    def test_request_extra_headers(self, connection, extra_headers):
        """Tests that the correct headers are passed when the headers argument is provided."""
        responses.add(
            url=connection.url("path"),
            method="POST",
            status=200,
            match=(matchers.header_matcher({**connection.headers, **extra_headers}),),
        )

        connection.request(method="POST", path="path", headers=extra_headers)

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

        match = r"Refresh token \(e\.g\.\, Xanadu Cloud API key\) is invalid"
        with pytest.raises(HTTPError, match=match) as excinfo:
            connection.update_access_token()
        assert hasattr(excinfo.value, "response")
        assert excinfo.value.response.status_code == 400
        assert excinfo.value.response.json()["error"] == "invalid_grant"

    @responses.activate
    def test_update_access_token_failure_due_to_status_code(self, connection):
        """Tests that an HTTPError is raised when the HTTP response to an access
        token request contains valid JSON but its status code indicates that an
        error occurred.
        """
        responses.add(
            responses.POST,
            connection.url("auth/realms/platform/protocol/openid-connect/token"),
            status=403,
            body="{}",
        )

        with pytest.raises(HTTPError, match=r"403 Client Error: Forbidden"):
            connection.update_access_token()
