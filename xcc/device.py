"""
This module contains the :class:`~xcc.Device` class.
"""

from typing import Any, Dict, List, Mapping
from urllib.parse import urlparse

from .connection import Connection


class Device:
    """Represents a device on the Xanadu Cloud.

    Args:
        target (str): target name of the device
        connection (Connection): connection to the Xanadu Cloud
        lazy (bool): fetch properties from the Xanadu Cloud on demand;
            specifying ``True`` can help conserve network bandwidth

    **Example:**

    The following example shows how to use the :class:`xcc.Device` class to
    query various properties of the X8_01 device on the Xanadu Cloud. First, a
    connection is established to the Xanadu Cloud:

    >>> import xcc
    >>> connection = xcc.Connection(key="Xanadu Cloud API key goes here")

    Next, a reference to the X8_01 device is created using the connection.

    >>> device = xcc.Device("X8_01", connection)

    Finally, the certificate, specification, status, etc. of the X8_01 device
    is retrieved by accessing the device's corresponding properties:

    >>> device.certificate
    {'device_url': ..., 'laser_wavelength_meters': 1.55270048e-06}
    >>> device.specification
    {'gate_parameters': ..., 'target': 'X8_01'}

    Note that, for performance reasons, the properties of a device are cached.
    This cache can be cleared by calling :meth:`~xcc.Device.refresh`.

    >>> device.refresh()
    """

    def __init__(self, target: str, connection: Connection, lazy: bool = True) -> None:
        self._target = target
        self._connection = connection
        self._lazy = lazy

        # Ideally, these private members would be replaced with @lru_cache
        # decorators on their corresponding properties; however, clearing
        # these caches on a per-instance basis is challenging because the
        # caches across each device are shared using this technique.
        self.__details = None
        self._certificate = None
        self._specification = None

        if not lazy:
            self._fetch()

    @property
    def connection(self) -> Connection:
        """Returns the connection used to access the Xanadu Cloud."""
        return self._connection

    @property
    def lazy(self) -> bool:
        """Returns whether a device only contacts the Xanadu Cloud on demand."""
        return self._lazy

    @property
    def target(self) -> str:
        """Returns the target of a device."""
        return self._target

    @property
    def _details(self) -> Dict[str, Any]:
        """Returns the details of a device.

        Returns:
            Dict[str, Any]: mapping from field names to values for this device

        .. note::

            These fields are not intended to be directly accessed by external
            callers. Instead, they should be individually retrieved through
            their associated public properties.
        """
        if self.__details is None:
            response = self.connection.request("GET", f"/devices/{self.target}")
            self.__details = response.json()

        return self.__details

    @property
    def certificate(self) -> Dict[str, Any]:
        """Returns the certificate of a device.

        A device certificate contains the current operating conditions of a
        device and is periodically updated while the device is online.

        Returns:
            Dict[str, Any]: certificate of this device

        .. note::

            After this property is accessed, :meth:`~xcc.Device.refresh()` must
            be called to fetch a new certificate from the Xanadu Cloud.

        .. warning::

            The structure of a certificate may vary from device to device.
        """
        if self._certificate is None:
            url = self._details["certificate_url"]
            path = urlparse(url).path

            response = self.connection.request("GET", path)
            self._certificate = response.json()

        return self._certificate

    @property
    def specification(self) -> Dict[str, Any]:
        """Returns the specification of a device.

        A device specification lists the hardware and sofware capabilities of a
        device and is not expected to change across the lifetime of a device.

        Returns:
            Dict[str, Any]: specification of this device

        .. note::

            After this property is accessed, :meth:`~xcc.Device.refresh()` must
            be called to fetch a new specification from the Xanadu Cloud.
        """
        if self._specification is None:
            url = self._details["specifications_url"]
            path = urlparse(url).path

            response = self.connection.request("GET", path)
            self._specification = response.json()

        return self._specification

    @property
    def expected_uptime(self) -> Mapping[str, List[str]]:
        """Returns the expected uptime of a device.

        Returns:
            Mapping[str, List[str]]: mapping from weekdays to time pairs where
            each pair represents when the device is expected to come online and
            offline that day
        """
        return self._details["expected_uptime"]

    @property
    def status(self) -> str:
        """Returns the current status of a device.

        Returns:
            str: status of this device ("online" or "offline")
        """
        return self._details["state"]

    # pylint: disable=invalid-name
    @property
    def up(self) -> bool:
        """Returns whether a device can currently accept jobs.

        Returns:
            bool: ``True`` if a device can accept jobs or ``False`` otherwise
        """
        return self._details["up"]

    def __repr__(self) -> str:
        """Returns a printable representation of a device."""
        return f"<{self.__class__.__name__}: target={self.target}>"

    def _fetch(self) -> None:
        """Caches the details, certificate, and specification of a device."""
        self.__details = self._details
        self._certificate = self.certificate
        self._specification = self.specification

    def refresh(self) -> None:
        """Refreshes the details, certificate, and specification of a device.

        .. note::

            This method supports both lazy and eager fetching strategies.
        """
        self.__details = None
        self._certificate = None
        self._specification = None

        if not self.lazy:
            self._fetch()
