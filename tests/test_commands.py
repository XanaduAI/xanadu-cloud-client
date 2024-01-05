# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.commands` module.
"""

import json
from inspect import cleandoc

import numpy as np
import pytest
from fire.core import FireError

import xcc
import xcc.commands
from xcc.util import cached_property


class MockDevice(xcc.Device):
    """Mock :class:`xcc.Device` class with an offline implementation of each
    property and function which is directly accessed by a CLI command.
    """

    @staticmethod
    def list(connection, status=None):
        connection = xcc.commands.load_connection()
        return [MockDevice(target, connection) for target in ("foo", "bar")]

    @property
    def overview(self):
        return {"target": self.target}

    @property
    def status(self):
        return "online"

    @cached_property
    def certificate(self):
        return {"temperature": "300 Kelvin"}

    @cached_property
    def specification(self):
        return {"modes": 42}


class MockJob(xcc.Job):
    """Mock :class:`xcc.Job` class with an offline implementation of each
    property and function which is directly accessed by a CLI command.
    """

    @staticmethod
    def list(connection, limit=10, ids=None, status=None):
        connection = xcc.commands.load_connection()
        return [MockJob(id_, connection) for id_ in ("foo", "bar", "baz")][:limit]

    @staticmethod
    def submit(connection, name, target, circuit, language="blackbird:1.0"):
        return MockJob(id_=name, connection=connection)

    @property
    def overview(self):
        return {"id": self.id}

    @property
    def status(self):
        return "cancelled"

    @property
    def circuit(self):
        return "MeasureFock() | [0, 1, 2, 3]"

    @property
    def language(self):
        return "blackbird:1.0"

    def get_result(self, integer_overflow_protection=True):
        return {"output": [np.zeros((4, 4))], "metadata": np.ones((2, 2))}

    def cancel(self):
        pass


@pytest.fixture(autouse=True)
def device(monkeypatch) -> None:
    """Replaces the :class:`xcc.Device` class with the :class:`MockDevice` class in the CLI."""
    monkeypatch.setattr("xcc.commands.Device", MockDevice)


@pytest.fixture(autouse=True)
def job(monkeypatch) -> None:
    """Replaces the :class:`xcc.Job` class with the :class:`MockJob` class in the CLI."""
    monkeypatch.setattr("xcc.commands.Job", MockJob)


@pytest.mark.usefixtures("settings")
def test_load_connection(monkeypatch):
    """Tests that a connection can be loaded."""
    monkeypatch.setattr("xcc.commands.__version__", "1.2.3-alpha")

    connection = xcc.commands.load_connection()
    assert connection.refresh_token == "j.w.t"
    assert connection.host == "example.com"
    assert connection.port == 80
    assert connection.tls is False
    assert connection.user_agent == "XCC/1.2.3-alpha (CLI)"


# Settings CLI
# ------------------------------------------------------------------------------


class TestGetSetting:
    """Tests the :func:`xcc.commands.get_setting()` CLI command."""

    def test_valid(self):
        """Tests that the value of a setting can be retrieved."""
        assert xcc.commands.get_setting(name="PORT") == 80

    def test_mixed_case(self):
        """Tests that the name of a setting is case-insensitive."""
        assert xcc.commands.get_setting(name="PoRt") == 80

    def test_invalid_name(self):
        """Tests that a ValueError is raised when the name of a setting is invalid."""
        with pytest.raises(ValueError, match=r"The setting name 'DNE' must be one of \[.*\]"):
            xcc.commands.get_setting(name="DNE")

    def test_missing_value(self, settings):
        """Tests that a ValueError is raised when the value of a setting is ``None``."""
        settings.ACCESS_TOKEN = None
        settings.save()

        match = r"The ACCESS_TOKEN setting does not currently have a value"
        with pytest.raises(ValueError, match=match):
            xcc.commands.get_setting(name="ACCESS_TOKEN")


def test_list_settings():
    """Tests that the :func:`xcc.commands.list_settings()` CLI command lists settings."""
    have_settings = json.loads(xcc.commands.list_settings())
    want_settings = {
        "REFRESH_TOKEN": "j.w.t",
        "ACCESS_TOKEN": None,
        "HOST": "example.com",
        "PORT": 80,
        "TLS": False,
    }
    assert have_settings == want_settings


class TestSetSetting:
    """Tests the :func:`xcc.commands.set_setting()` CLI command."""

    def test_valid(self):
        """Tests that the value of a setting can be updated."""
        xcc.commands.set_setting(name="PORT", value=123)
        assert xcc.Settings().PORT == 123

    def test_mixed_case(self):
        """Tests that the name of a setting is case-insensitive."""
        xcc.commands.set_setting(name="PoRt", value=123)
        assert xcc.Settings().PORT == 123

    @pytest.mark.parametrize(
        "name, value, message",
        [
            ("TLS", True, "Successfully updated TLS setting to True."),
            ("PORT", 123, "Successfully updated PORT setting to 123."),
            ("HOST", "foo", "Successfully updated HOST setting to 'foo'."),
        ],
    )
    def test_message(self, name, value, message):
        """Tests that the correct message is displayed when a setting is updated."""
        assert xcc.commands.set_setting(name=name, value=value) == message

    def test_invalid_name(self):
        """Tests that a ValueError is raised when the name of a setting is invalid."""
        with pytest.raises(ValueError, match=r"The setting name 'DNE' must be one of \[.*\]\."):
            xcc.commands.set_setting(name="DNE", value="N/A")

    def test_invalid_value(self):
        """Tests that a ValueError is raised when the value of a setting is invalid."""
        match = (
            r"Failed to update PORT setting: "
            r"Input should be a valid integer, unable to parse string as an integer"
        )
        with pytest.raises(ValueError, match=match):
            xcc.commands.set_setting(name="PORT", value="string")


# Device CLI
# ------------------------------------------------------------------------------


class TestGetDevice:
    """Tests the :func:`xcc.commands.get_device()` CLI command."""

    def test_overview(self):
        """Tests that the overview of a device can be retrieved."""
        have_overview = json.loads(xcc.commands.get_device(target="foo"))
        want_overview = {"target": "foo"}
        assert have_overview == want_overview

    def test_status(self):
        """Tests that the status of a device can be retrieved."""
        assert xcc.commands.get_device(target="foo", status=True) == "online"

    def test_certificate(self):
        """Tests that the certificate of a device can be retrieved."""
        have_certificate = json.loads(xcc.commands.get_device(target="foo", certificate=True))
        want_certificate = {"temperature": "300 Kelvin"}
        assert have_certificate == want_certificate

    def test_specification(self):
        """Tests that the specification of a device can be retrieved."""
        have_specification = json.loads(xcc.commands.get_device(target="foo", specification=True))
        want_specification = {"modes": 42}
        assert have_specification == want_specification

    def test_invalid_number_of_flags(self):
        """Tests that a FireError is raised when more than one flag is specified."""
        with pytest.raises(FireError, match=r"At most one device property can be selected"):
            xcc.commands.get_device(target="foo", status=True, certificate=True)


def test_list_devices():
    """Tests that the :func:`xcc.commands.list_devices()` CLI command lists devices."""
    have_list = json.loads(xcc.commands.list_devices())
    want_list = [{"target": "foo"}, {"target": "bar"}]
    assert have_list == want_list


# Job CLI
# ------------------------------------------------------------------------------


class TestCancelJob:
    """Tests the :func:`xcc.commands.cancel_job()` CLI command."""

    def test_cancel_success(self):
        """Tests that the correct message is displayed when a job was cancelled."""
        have_message = xcc.commands.cancel_job(id="foo")
        want_message = "Successfully cancelled job with ID 'foo'."
        assert have_message == want_message

    def test_cancel_failure(self, monkeypatch):
        """Tests that a ValueError is raised if a job could not be cancelled."""
        monkeypatch.setattr("xcc.commands.Job.status", "completed")
        with pytest.raises(ValueError, match=r"Job with ID 'foo' was not cancelled in time\."):
            xcc.commands.cancel_job(id="foo")


class TestGetJob:
    """Tests the :func:`xcc.commands.get_job()` CLI command."""

    def test_overview(self):
        """Tests that the overview of a job can be retrieved."""
        have_overview = json.loads(xcc.commands.get_job(id="foo"))
        want_overview = {"id": "foo"}
        assert have_overview == want_overview

    def test_status(self):
        """Tests that the status of a job can be retrieved."""
        assert xcc.commands.get_job(id="foo", status=True) == "cancelled"

    def test_circuit(self):
        """Tests that the circuit of a job can be retrieved."""
        assert xcc.commands.get_job(id="foo", circuit=True) == "MeasureFock() | [0, 1, 2, 3]"

    def test_result(self):
        """Tests that the result of a job can be retrieved."""
        have_result = xcc.commands.get_job(id="foo", result=True)
        want_result = cleandoc(
            """
            {
                "metadata": [[1.0, 1.0], [1.0, 1.0]],
                "output": [[[0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0]]]
            }
            """
        )
        assert have_result == want_result

    def test_invalid_number_of_flags(self):
        """Tests that a FireError is raised when more than one flag is specified."""
        with pytest.raises(FireError, match=r"At most one job property can be selected"):
            xcc.commands.get_job(id="foo", status=True, result=True)


def test_list_jobs():
    """Tests that the :func:`xcc.commands.list_jobs()` CLI command lists jobs."""
    have_list = json.loads(xcc.commands.list_jobs(limit=2))
    want_list = [{"id": "foo"}, {"id": "bar"}]
    assert have_list == want_list


def test_submit_job():
    """Tests that a job can be submitted using the :func:`xcc.commands.submit_job()` CLI command."""
    have_overview = json.loads(xcc.commands.submit_job(name="foo", target="bar", circuit="baz"))
    want_overview = {"id": "foo"}
    assert have_overview == want_overview


# Other CLI
# ------------------------------------------------------------------------------


def test_ping(monkeypatch):
    """Tests that the output of the :func:`xcc.commands.ping()` command
    is correct when the connection to the Xanadu Cloud is successful.
    """
    monkeypatch.setattr("xcc.commands.Connection.ping", lambda _: None)
    assert xcc.commands.ping() == "Successfully connected to the Xanadu Cloud."


def test_version(monkeypatch):
    """Tests that the output of the :func:`xcc.commands.version()` command
    has the correct form.
    """
    monkeypatch.setattr("xcc.commands.__version__", "1.2.3-alpha")
    assert xcc.commands.version() == "Xanadu Cloud Client version 1.2.3-alpha"
