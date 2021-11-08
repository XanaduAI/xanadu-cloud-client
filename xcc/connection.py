"""
This module contains the :class:`~xcc.Connection` class.
"""
from itertools import chain
from typing import Dict, List, Optional

import requests

from ._version import __version__


class Connection:
    """Manages remote connections to the Xanadu Cloud.

    Args:
        refresh_token (str, optional): JWT refresh token, such as a Xanadu Cloud
            API key, that is used to fetch access tokens from the Xanadu Cloud
        access_token (str, optional): JWT access token that is used to
            authenticate requests to the Xanadu Cloud; missing, invalid, or
            expired access tokens are replaced using the refresh token
        host (str): hostname of the Xanadu Cloud server
        port (int): port of the Xanadu Cloud server
        tls (bool): whether to use HTTPS for the connection
        headers (Dict[str, str], optional): HTTP request headers to override

    Raises:
        ValueError: if both the refresh token and access token are ``None``

    **Example:**

    The following example shows how to use the :class:`~xcc.Connection` class
    to access the Xanadu Cloud. First, a connection is instantiated with a
    Xanadu Cloud API key:

    >>> import xcc
    >>> connection = xcc.Connection(refresh_token="Xanadu Cloud API key goes here")

    This connection can be tested using :meth:`~xcc.Connection.ping`. If there
    is an issue with the connection, a :exc:`requests.models.HTTPError` will be
    raised.

    >>> connection.ping()
    <Response [200]>

    The Xanadu Cloud can now be directly accessed to, for example, retrieve
    information about the X8_01 device:

    >>> response = connection.request(method="GET", path="/devices/X8_01")
    >>> response
    <Response [200]>
    >>> import json
    >>> print(json.dumps(response.json(), indent=4))
    {
        "expected_uptime": {
            "monday": [
                "15:00:00+00:00",
                "22:59:59+00:00"
            ],
            "tuesday": [
                "15:00:00+00:00",
                "22:59:59+00:00"
            ],
            "thursday": [
                "15:00:00+00:00",
                "22:59:59+00:00"
            ],
            "wednesday": [
                "15:00:00+00:00",
                "22:59:59+00:00"
            ]
        },
        "created_at": "2021-01-27T15:15:25.801308Z",
        "target": "X8_01",
        "status": "online"
    }
    """

    def __init__(
        self,
        refresh_token: Optional[str] = None,
        access_token: Optional[str] = None,
        host: str = "platform.strawberryfields.ai",
        port: int = 443,
        tls: bool = True,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        if refresh_token is None and access_token is None:
            raise ValueError(
                "A refresh token (e.g., Xanadu Cloud API key) or an access "
                "token must be provided to connect to the Xanadu Cloud."
            )

        self._access_token = access_token
        self._refresh_token = refresh_token

        self._tls = tls
        self._host = host
        self._port = port

        self._headers = headers or {}

    @property
    def access_token(self) -> Optional[str]:
        """Returns the access token used to authenticate requests to the Xanadu Cloud."""
        return self._access_token

    @property
    def refresh_token(self) -> Optional[str]:
        """Returns the refresh token used to fetch access tokens."""
        return self._refresh_token

    @property
    def tls(self) -> bool:
        """Returns whether HTTPS is used for the connection to the Xanadu Cloud."""
        return self._tls

    @property
    def scheme(self) -> str:
        """Returns the scheme of the URL used to send requests to the Xanadu Cloud."""
        return "https" if self._tls else "http"

    @property
    def host(self) -> str:
        """Returns the host of the URL used to send requests to the Xanadu Cloud."""
        return self._host

    @property
    def port(self) -> int:
        """Returns the port of the URL used to send requests to the Xanadu Cloud"""
        return self._port

    @property
    def api_version(self) -> str:
        """Returns the "Accept-Version" header included in requests to the Xanadu Cloud."""
        return self._headers.get("Accept-Version", "0.4.0")

    @property
    def user_agent(self) -> str:
        """Returns the "User-Agent" header included in requests to the Xanadu Cloud."""
        return self._headers.get("User-Agent", f"XCC/{__version__} (API)")

    @property
    def headers(self) -> Dict[str, str]:
        """Returns the headers included in requests to the Xanadu Cloud."""
        return {
            "Accept-Version": self.api_version,
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent,
            **self._headers,
        }

    def __repr__(self) -> str:
        """Returns a printable representation of a connection."""
        return (
            f"<{self.__class__.__name__}: "
            f"refresh_token={self.refresh_token}, "
            f"access_token={self.access_token}, "
            f"url={self.url()}>"
        )

    def url(self, path: str = "") -> str:
        """Returns the URL to a Xanadu Cloud endpoint.

        Args:
            path (str): path component of the URL

        Returns:
            str: URL containing a scheme, host, port, the provided path
        """
        return f"{self.scheme}://{self.host}:{self.port}/" + path.lstrip("/")

    def ping(self) -> requests.Response:
        """Pings the Xanadu Cloud.

        Returns:
            requests.Response: HTTP response of the ping HTTP request

        Raises:
            requests.exceptions.RequestException: if there was an issue sending
                the ping request to the Xanadu Cloud or the status code of the
                HTTP response indicates that an error occurred (i.e., 4XX or 5XX)
        """
        return self.request(method="GET", path="/healthz")

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Sends an HTTP request to the Xanadu Cloud.

        Args:
            method (str): HTTP request method
            path (str): HTTP request path
            **kwargs: optional arguments to pass to :func:`requests.request()`

        Returns:
            requests.Response: HTTP response to the HTTP request

        Raises:
            requests.exceptions.RequestException: if there was an issue sending
                the HTTP request or the status code of the HTTP response
                indicates that an error occurred (i.e., 4XX or 5XX)

        .. note::

            A second HTTP request will be made to the Xanadu Cloud if the HTTP
            response to the first request has a 401 status code. The second
            request will be identical to the first one except that a fresh
            access token will be used.
        """
        url = self.url(path)

        response = self._request(method=method, url=url, headers=self.headers, **kwargs)

        if response.status_code == 401:
            self.update_access_token()
            response = self._request(method=method, url=url, headers=self.headers, **kwargs)

        try:
            body = response.json()

        except Exception:  # pylint: disable=broad-except
            # Until https://github.com/psf/requests/pull/5856 is deployed, the
            # requests package (2.26.0) can raise one of several different types
            # of exceptions when parsing JSON (including a third-party type).
            response.raise_for_status()

        else:
            # The details of a validation error are encoded in the "meta" field.
            if response.status_code == 400 and body.get("code", "") == "validation-error":
                errors: Dict[str, List[str]] = body.get("meta", {})
                if errors:
                    message = "; ".join(chain.from_iterable(errors.values()))
                    raise requests.exceptions.HTTPError(message, response=response)

            # Otherwise, the details of the error may be encoded in the "detail" field.
            if not response.ok and "detail" in body:
                message = body["detail"]
                raise requests.exceptions.HTTPError(message, response=response)

            response.raise_for_status()

        return response

    def update_access_token(self) -> None:
        """Updates the access token of a connection using its refresh token.

        Raises:
            requests.exceptions.RequestException: if there was an issue sending
                the HTTP request for the access token or the status code of the
                HTTP response indicates that an error occurred (i.e., 4XX or 5XX)
        """
        url = self.url("/auth/realms/platform/protocol/openid-connect/token")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": "public",
        }

        response = self._request(method="POST", url=url, data=data)

        try:
            body = response.json()

        except Exception as exc:  # pylint: disable=broad-except
            # See Connection.request() for why exceptions are broadly caught.
            response.raise_for_status()
            # The following ValueError is only raised if the Xanadu Cloud
            # authentication service is acting unexpectedly.
            raise ValueError("Xanadu Cloud returned an invalid access token response.") from exc

        else:
            # It is worth investing in a helpful error message for invalid API
            # keys since most users will likely encounter it at some point.
            if response.status_code == 400 and body.get("error", "") == "invalid_grant":
                raise requests.exceptions.HTTPError(
                    "Refresh token (e.g., Xanadu Cloud API key) is invalid"
                )

            response.raise_for_status()

        self._access_token = body.get("access_token")

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Sends an HTTP request.

        Args:
            method (str): HTTP request method
            path (str): HTTP request path
            **kwargs: optional arguments to pass to :func:`requests.request()`

        Returns:
            requests.Response: HTTP response to the HTTP request

        Raises:
            requests.exceptions.RequestException: if there was an issue sending
                the HTTP request

        .. note::

            No validation is performed on the status code of the HTTP response.

        .. warning::

            The delay between when this function is called and when a timeout
            exception is raised will be (slightly greater than) a multiple of
            the ``timeout`` parameter passed to :func:`requests.request()`.
            Specifically, if the timeout value is :math:`t` and there are
            :math:`r` resource records listed for the hostname and port of the
            Xanadu Cloud, then :math:`\\approx tr` seconds will elapse before a
            timeout is detected.
        """
        try:
            timeout = kwargs.pop("timeout", 10)
            return requests.request(method=method, url=url, timeout=timeout, **kwargs)

        except requests.exceptions.Timeout as exc:
            message = f"{method} request to '{url}' timed out"
            raise requests.exceptions.RequestException(message) from exc

        except requests.exceptions.ConnectionError as exc:
            if "Name or service not known" in str(exc):
                message = f"Failed to resolve hostname '{self.host}'"
                raise requests.exceptions.RequestException(message) from exc
            raise exc
