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

    def test_target(self, device):
        """Tests that the correct target is returned for a device."""
        assert device.target == "qpu"

    @responses.activate
    def test_certificate(self, device, add_device_response):
        """Tests that the correct certificate is returned for a device."""
        add_device_response({"certificate_url": "https://example.com/devices/qpu/certificate"})

        url = device.connection.url("/devices/qpu/certificate")
        responses.add(responses.GET, url, status=200, body='{"conditions": "nominal"}')

        assert device.certificate == {"conditions": "nominal"}

    @responses.activate
    def test_specification(self, device, add_device_response):
        """Tests that the correct specification is returned for a device."""
        add_device_response({"specifications_url": "https://example.com/devices/qpu/specification"})

        url = device.connection.url("/devices/qpu/specification")
        responses.add(responses.GET, url, status=200, body='{"compiler": "LLVM", "modes": 42}')

        assert device.specification == {"compiler": "LLVM", "modes": 42}

    @responses.activate
    def test_expected_uptime(self, device, add_device_response):
        """Tests that the correct expected uptime is returned for a device."""
        add_device_response({"expected_uptime": {"monday": ["16:00:00+00:00", "23:59:59+00:00"]}})
        assert device.expected_uptime == {"monday": ["16:00:00+00:00", "23:59:59+00:00"]}

    @responses.activate
    @pytest.mark.parametrize("status", ["offline", "online"])
    def test_status(self, device, add_device_response, status):
        """Tests that the correct status is returned for a device."""
        add_device_response({"state": status})
        assert device.status == status

    @responses.activate
    @pytest.mark.parametrize("up", [False, True])
    def test_up(self, device, add_device_response, up):
        """Tests that the correct up indicator is returned for a device."""
        add_device_response({"up": up})
        assert device.up == up

    @responses.activate
    def test_refresh_lazy(self, device, add_device_response):
        """Tests that the cache of a device can be lazily refreshed."""
        add_device_response({"up": False})
        add_device_response({"up": True})

        assert device.up is False
        assert device.up is False

        device.refresh(lazy=True)

        assert len(responses.calls) == 1
        assert device.up is True

    @responses.activate
    def test_refresh_eager(self, device, add_device_response):
        """Tests that the cache of a device can be eagerly refreshed."""
        add_device_response({"up": False})
        add_device_response({"up": True, "certificate_url": "/cert", "specifications_url": "/spec"})
        responses.add(responses.GET, device.connection.url("/cert"), status=200, body="{}")
        responses.add(responses.GET, device.connection.url("/spec"), status=200, body="{}")

        assert device.up is False
        assert device.up is False

        device.refresh(lazy=False)

        assert len(responses.calls) == 4
        assert device.up is True

    @responses.activate
    def test_refresh_scope(self, add_device_response, connection):
        """Tests that refreshing the cache of one device does not affect the
        cache of another device.
        """
        device_1 = xcc.Device("qpu", connection)
        device_2 = xcc.Device("qpu", connection)

        add_device_response({"up": False})
        add_device_response({"up": False})
        add_device_response({"up": True})

        assert device_1.up is False
        assert device_2.up is False

        device_1.refresh()

        assert device_1.up is True
        assert device_2.up is False
