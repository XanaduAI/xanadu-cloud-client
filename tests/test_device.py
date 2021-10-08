# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.device` module.
"""

import json
from datetime import time
from typing import Callable

import pytest
import responses

import xcc


@pytest.fixture
def device(connection) -> xcc.Device:
    """Returns a mock device with the given connection."""
    return xcc.Device("qpu", connection)


@pytest.fixture
def add_response(connection) -> Callable[[object, str], None]:
    """Returns a function that places a JSON serialization of its argument
    inside the body of an HTTP 200 response to the next GET request to the
    specified path ("/devices/qpu" by default) using the given connection.
    """

    def add_response_(body: object, path: str = "/devices/qpu") -> None:
        url = connection.url(path)
        return responses.add(responses.GET, url, status=200, body=json.dumps(body))

    return add_response_


class TestDevice:
    """Tests the :class:`xcc.Device` class."""

    @pytest.mark.parametrize(
        "status, want_targets",
        [(None, ["foo", "bar"]), ("online", ["foo"]), ("offline", ["bar"])],
    )
    @responses.activate
    def test_list(self, connection, add_response, status, want_targets):
        """Tests that the correct devices are listed for a status."""
        data = [
            {"target": "foo", "status": "online"},
            {"target": "bar", "status": "offline"},
        ]
        add_response(body={"data": data}, path="/devices")

        have_targets = [device.target for device in xcc.Device.list(connection, status)]
        assert have_targets == want_targets

    def test_target(self, device):
        """Tests that the correct target is returned for a device."""
        assert device.target == "qpu"

    @responses.activate
    def test_overview(self, device, add_response):
        """Tests that the correct overview is returned for a device."""
        add_response(body={"target": "qpu", "status": "online"})
        assert device.overview == {"target": "qpu", "status": "online"}

    @responses.activate
    def test_certificate(self, device, add_response):
        """Tests that the correct certificate is returned for a device."""
        add_response(body={"conditions": "nominal"}, path="/devices/qpu/certificate")
        assert device.certificate == {"conditions": "nominal"}

    @responses.activate
    def test_specification(self, device, add_response):
        """Tests that the correct specification is returned for a device."""
        add_response(body={"compiler": "LLVM", "modes": 42}, path="/devices/qpu/specifications")
        assert device.specification == {"compiler": "LLVM", "modes": 42}

    @responses.activate
    def test_expected_uptime(self, device, add_response):
        """Tests that the correct expected uptime is returned for a device."""
        time_up = time.fromisoformat("16:00:00+00:00")
        time_dn = time.fromisoformat("20:00:00+00:00")
        times = [str(time_up), str(time_dn)]

        add_response(body={"expected_uptime": {"wednesday": times}})

        # Take care to verify the iteration order of the expected items.
        have_expected_uptime = list(device.expected_uptime.items())
        want_expected_uptime = [
            ("monday", None),
            ("tuesday", None),
            ("wednesday", (time_up, time_dn)),
            ("thursday", None),
            ("friday", None),
            ("saturday", None),
            ("sunday", None),
        ]

        assert have_expected_uptime == want_expected_uptime

    @responses.activate
    @pytest.mark.parametrize("status", ["offline", "online"])
    def test_status(self, device, add_response, status):
        """Tests that the correct status is returned for a device."""
        add_response(body={"status": status})
        assert device.status == status

    @responses.activate
    @pytest.mark.parametrize("status, up", [("offline", False), ("online", True)])
    def test_up(self, device, add_response, status, up):  # pylint: disable=invalid-name
        """Tests that the correct "up" indicator is returned for a device."""
        add_response(body={"status": status})
        assert device.up == up

    def test_repr(self, device):
        """Tests that the printable representation of a device is correct."""
        assert repr(device) == "<Device: target=qpu>"

    @responses.activate
    def test_clear(self, device, add_response):
        """Tests that the cache of a device can be cleared."""
        add_response(body={"status": "offline"})
        add_response(body={"status": "online"})

        assert device.status == "offline"
        assert device.status == "offline"

        device.clear()

        assert len(responses.calls) == 1
        assert device.status == "online"
        assert len(responses.calls) == 2

    @responses.activate
    def test_cache_independence(self, connection, add_response):
        """Tests that caches are not shared across device instances."""
        add_response(body={"status": "offline"})
        add_response(body={"status": "online"})
        add_response(body={"status": "online"})
        add_response(body={"status": "offline"})

        device_1 = xcc.Device("qpu", connection)
        device_2 = xcc.Device("qpu", connection)

        assert device_1.status == "offline"
        assert device_2.status == "online"
        assert len(responses.calls) == 2

        device_1.clear()

        assert device_1.status == "online"
        assert device_2.status == "online"
        assert len(responses.calls) == 3

        device_2.clear()

        assert device_1.status == "online"
        assert device_2.status == "offline"
        assert len(responses.calls) == 4
