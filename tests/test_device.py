# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.device` module.
"""

import json
from typing import Callable

import pytest
import responses

import xcc


@pytest.fixture
def device(connection) -> xcc.Device:
    """Returns a mock device with the given connection."""
    return xcc.Device("qpu", connection)


@pytest.fixture
def add_device_response(connection) -> Callable[[object], None]:
    """Returns a function that places a JSON serialization of its argument
    inside the body of an HTTP 200 response to the next GET request to the
    "/devices/qpu" path of the given connection's URL.
    """
    url = connection.url("/devices/qpu")
    return lambda body: responses.add(responses.GET, url, status=200, body=json.dumps(body))


class TestDevice:
    """Tests the :class:`xcc.Device` class."""

    def test_connection(self, connection):
        """Tests that the correct connection is returned for a device."""
        device = xcc.Device("qpu", connection)
        assert device.connection == connection

    def test_lazy(self, device):
        """Tests that the correct laziness indicator is returned for a device."""
        assert device.lazy is True

    def test_target(self, device):
        """Tests that the correct target is returned for a device."""
        assert device.target == "qpu"

    @responses.activate
    def test_certificate(self, device, add_response):
        """Tests that the correct certificate is returned for a device."""
        add_response(body={"certificate_url": "https://example.com/devices/qpu/certificate"})
        add_response(body={"conditions": "nominal"}, path="/devices/qpu/certificate")
        assert device.certificate == {"conditions": "nominal"}

    @responses.activate
    def test_specification(self, device, add_response):
        """Tests that the correct specification is returned for a device."""
        add_response(body={"specifications_url": "https://example.com/devices/qpu/specification"})
        add_response(body={"compiler": "LLVM", "modes": 42}, path="/devices/qpu/specification")
        assert device.specification == {"compiler": "LLVM", "modes": 42}

    @responses.activate
    def test_expected_uptime(self, device, add_response):
        """Tests that the correct expected uptime is returned for a device."""
        add_response(body={"expected_uptime": {"monday": ["16:00:00+00:00", "23:59:59+00:00"]}})
        assert device.expected_uptime == {"monday": ["16:00:00+00:00", "23:59:59+00:00"]}

    @responses.activate
    @pytest.mark.parametrize("status", ["offline", "online"])
    def test_status(self, device, add_response, status):
        """Tests that the correct status is returned for a device."""
        add_response(body={"state": status})
        assert device.status == status

    def test_repr(self, device):
        """Tests that the printable representation of a device is correct."""
        assert repr(device) == "<Device: target=qpu>"

    @responses.activate
    def test_refresh_lazy(self, add_response, connection):
        """Tests that the cache of a device can be lazily refreshed."""
        add_response(body={"state": "offline"})
        add_response(body={"state": "online"})

        device = xcc.Device("qpu", connection, lazy=True)

        assert device.status == "offline"
        assert device.status == "offline"

        device.refresh()

        assert len(responses.calls) == 1
        assert device.status == "online"
        assert len(responses.calls) == 2

    @responses.activate
    def test_refresh_eager(self, add_response, connection):
        """Tests that the cache of a device can be eagerly refreshed."""
        paths = {"certificate_url": "/cert", "specifications_url": "/spec"}
        add_response(body={"state": "offline", **paths})
        add_response(body={"state": "online", **paths})
        add_response(body={}, path="/cert")
        add_response(body={}, path="/spec")

        device = xcc.Device("qpu", connection, lazy=False)

        assert device.status == "offline"
        assert device.status == "offline"

        device.refresh()

        assert len(responses.calls) == 6
        assert device.status == "online"
        assert len(responses.calls) == 6

    @responses.activate
    def test_refresh_scope(self, add_response, connection):
        """Tests that refreshing the cache of one device does not affect the cache of another."""
        add_response(body={"state": "offline"})
        add_response(body={"state": "offline"})
        add_response(body={"state": "online"})

        device_1 = xcc.Device("qpu", connection)
        device_2 = xcc.Device("qpu", connection)

        assert device_1.status == "offline"
        assert device_2.status == "offline"

        device_1.refresh()

        assert device_1.status == "online"
        assert device_2.status == "offline"
