"""
This module contains the :class:`~xcc.Connection` class.
"""

from typing import Dict, Optional

import requests

from ._version import __version__


class XanaduCloudConnectionError(Exception):
    """Raised when a request to the Xanadu Cloud is unsuccessful."""


class Connection:
    """Manages remote connections to the Xanadu Cloud.

    Args:
        key (str): The Xanadu Cloud API key used for authentication.
        host (str): The hostname of the Xanadu Cloud server.
        port (int): The port of the Xanadu Cloud server.
        tls (bool): Whether to use HTTPS for the connection.

    **Example:**

    The following example shows how to use the :class:`~xcc.Connection` class.
    First, we instantiate a connection with a Xanadu Cloud API key:

    >>> import xcc
    >>> connection = xcc.Connection(key="Xanadu Cloud API key goes here")

    Next, we test the connection to the Xanadu Cloud using the
    :class:`~xcc.Connection.ping` method:

    >>> connection.ping()
    True

    Finally, we call the Xanadu Cloud API directly to retrieve information about
    the X8_01 device:

    >>> response = connection.request(method="GET", path="/devices/X8_01")
    >>> response.status_code
    200
    >>> import pprint
    >>> pp = pprint.PrettyPrinter(indent=4)
    >>> pp.pprint(response.json())
    {   'certificate_url': 'https://platform.strawberryfields.ai/devices/X8_01/certificate',
        'created_at': '2021-01-27T15:15:25.801308Z',
        'expected_uptime': {   'monday': ['16:00:00+00:00', '23:59:59+00:00'],
                               'thursday': ['16:00:00+00:00', '23:59:59+00:00'],
                               'tuesday': ['16:00:00+00:00', '23:59:59+00:00'],
                               'wednesday': ['16:00:00+00:00', '23:59:59+00:00']},
        'specifications_url': 'https://platform.strawberryfields.ai/devices/X8_01/specifications',
        'state': 'online',
        'target': 'X8_01',
        'up': True,
        'url': 'https://platform.strawberryfields.ai/devices/X8_01'}
    """

    def __init__(
        self,
        key: str,
        host: str = "platform.strawberryfields.ai",
        port: int = 443,
        tls: bool = True,
    ):
        self._access_token = None
        self._refresh_token = key

        self._tls = tls
        self._host = host
        self._port = port

    @property
    def access_token(self) -> str:
        """Returns the access token used to authorize requests to the Xanadu Cloud."""
        return self._access_token

    @property
    def refresh_token(self) -> Optional[str]:
        """Returns the refresh token (API key) used to fetch access tokens."""
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
        return "0.4.0"

    @property
    def user_agent(self) -> str:
        """Returns the "User-Agent" header included in requests to the Xanadu Cloud."""
        return f"XanaduCloudClient/{__version__}"

    @property
    def headers(self) -> Dict[str, str]:
        """Returns the headers included in requests to the Xanadu Cloud."""
        return {
            "Accept-Version": self.api_version,
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent,
        }

    def __repr__(self) -> str:
        """Returns a printable representation of a connection."""
        return f"<{self.__class__.__name__}: key={self.refresh_token}, url={self.url()}>"

    def __str__(self) -> str:
        """Returns a string representation of a connection."""
        return repr(self)

    def url(self, path: str = "") -> str:
        """Returns the URL to a Xanadu Cloud endpoint.

        Args:
            path (str): Path component of the URL.

        Returns:
            str: URL containing a scheme, host, port, the provided path.
        """
        return f"{self.scheme}://{self.host}:{self.port}/" + path.lstrip("/")

    def ping(self) -> bool:
        """Pings the Xanadu Cloud.

        Returns:
            bool: ``True`` if the connection is successful and ``False`` otherwise.
        """
        response = self.request(method="GET", path="/healthz")
        return response.status_code == 200

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Sends an HTTP request to the Xanadu Cloud.

        Args:
            method (str): HTTP request method.
            path (str): HTTP request path.

        Keyword Args:
            Arguments to pass along to the call to ``requests.request()``.

        Returns:
            requests.Response: HTTP response of the HTTP request.

        .. note::

            A second HTTP request will be made to the Xanadu Cloud if the first
            one returned status code 401. The second request will be identical
            to the first one except a fresh access token will be used.
        """
        url = self.url(path)

        response = requests.request(method=method, url=url, headers=self.headers, **kwargs)

        if response.status_code == 401:
            self.update_access_token()
            response = requests.request(method=method, url=url, headers=self.headers, **kwargs)

        return response

    def update_access_token(self) -> None:
        """Updates the access token of a connection using its refresh token.

        Raises:
            XanaduCloudConnectionError: If the access token could not be updated.
        """
        url = self.url("/auth/realms/platform/protocol/openid-connect/token")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token,
            "client_id": "public",
        }
        response = requests.post(url=url, data=data)

        if response.status_code == 200:
            self._access_token = response.json().get("access_token")
        else:
            raise XanaduCloudConnectionError(
                "Failed to update access token. Ensure that your Xanadu Cloud API key is correct."
            )
