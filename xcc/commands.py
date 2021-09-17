"""
This module implements the Xanadu Cloud CLI.
"""

import functools
import json
import sys
from typing import Any, Callable, Tuple, Union

import fire
from fire.core import FireError
from fire.formatting import Error
from pydantic import ValidationError

from ._version import __version__
from .connection import Connection
from .device import Device
from .job import Job
from .settings import Settings


def beautify(command: Callable) -> Callable:
    """Decorator which formats the output of a CLI command.

    Args:
        command (Callable): function which implements a CLI command

    Returns:
        Callable: CLI command which converts the value returned by the given
        CLI command into a JSON string if the value is a list or dictionary
    """

    @functools.wraps(command)
    def beautify_(*args, **kwargs):
        output = command(*args, **kwargs)
        if isinstance(output, (list, dict)):
            return json.dumps(output, indent=4, sort_keys=True, default=str)
        return output

    return beautify_


# Settings CLI
# ------------------------------------------------------------------------------


@beautify
def get_setting(name: str):
    """Gets the value of a setting.

    Args:
        name (str): Name of the setting (e.g., "API_KEY").
    """
    key, val = _resolve_setting(name)

    if val is None:
        raise ValueError(f"The {key} setting does not currently have a value.")

    return val


@beautify
def list_settings():
    """Lists the current settings."""
    return Settings().dict()


@beautify
def set_setting(name: str, value: Union[str, int, bool]):
    """Sets the value of a setting.

    Args:
        name (str): Name of the setting (e.g., "PORT").
        value (str, int, bool): Value of the setting (e.g., 443).
    """
    key, _ = _resolve_setting(name)

    try:
        Settings(**{key: value}).save()
    except ValidationError as exc:
        err = exc.errors()[0].get("msg", "invalid value")
        raise ValueError(f"Failed to update {key} setting: {err}") from exc


def _resolve_setting(name: str) -> Tuple[str, Any]:
    """Resolves the key and value of a setting.

    Args:
        name (str): name of the setting

    Returns:
        Tuple[str, Any]: resolved key and value of the setting

    Raises:
        ValueError: if the name of the setting is invalid
    """
    key = name.upper()

    settings = Settings()
    if key not in settings.dict():
        raise ValueError(f"The setting name '{name}' must be one of {list(settings.dict())}.")

    return key, settings.dict()[key]


# Device CLI
# ------------------------------------------------------------------------------


@beautify
def get_device(
    target: str,
    certificate: bool = False,
    specification: bool = False,
    status: bool = False,
):
    """Gets information about a device on the Xanadu Cloud.

    If no device property flags are specified, an overview of the device is
    displayed. Otherwise, only the selected device property is shown.

    Args:
        target (str): Name of the device target.
        certificate (bool): Show the certificate of the device.
        specification (bool): Show the specification of the device.
        status (bool): Show the status of the device.
    """
    device = Device(target, Connection.load())

    flags = sum([certificate, specification, status])
    if flags > 1:
        raise FireError("At most one device property can be selected.")

    if flags == 0:
        return device.overview
    if status:
        return device.status
    if certificate:
        return device.certificate
    if specification:
        return device.specification

    raise NotImplementedError


@beautify
def list_devices(status: str = None):
    """Lists devices on the Xanadu Cloud.

    Args:
        status (str): Filter devices by status (e.g., "offline" or "online").
    """
    devices = Device.list(connection=Connection.load(), status=status)
    return [device.overview for device in devices]


# Job CLI
# ------------------------------------------------------------------------------


@beautify
# pylint: disable=invalid-name,redefined-builtin
def get_job(id: str, circuit: bool = False, result: bool = False, status: bool = False):
    """Gets information about a job on the Xanadu Cloud.

    If no job property flags are specified, an overview of the job is
    displayed. Otherwise, only the selected job property is shown.

    Args:
        id (str): ID of the job.
        circuit (bool): Show the circuit of the job.
        result (bool): Show the result of the job.
        status (bool): Show the status of the job.
    """
    job = Job(id_=id, connection=Connection.load())

    flags = sum([circuit, result, status])
    if flags > 1:
        raise FireError("At most one job property can be selected.")

    if flags == 0:
        return job.overview
    if circuit:
        return {"circuit": job.circuit, "language": job.language}
    if status:
        return job.status
    if result:
        return str(job.result)

    raise NotImplementedError


@beautify
def list_jobs(limit: int = 10):
    """Lists jobs submitted to the Xanadu Cloud.

    Args:
        limit (int): Maximum number of jobs to display.
    """
    jobs = Job.list(connection=Connection.load(), limit=limit)
    return [job.overview for job in jobs]


@beautify
def submit_job(name: str, target: str, circuit: str, language: str = "blackbird:1.0"):
    """Submits a job to the Xanadu Cloud.

    Args:
        name (str): Name of the job.
        target (str): Target of the job.
        circuit (str): Circuit of the job.
        language (str): Language of the job.
    """
    job = Job.submit(
        connection=Connection.load(),
        name=name,
        target=target,
        circuit=circuit.replace("\\n", "\n"),
        language=language,
    )
    return job.overview


# Other CLI
# ------------------------------------------------------------------------------


def ping():
    """Tests the connection to the Xanadu Cloud."""
    Connection.load().ping()
    return "Successfully connected to the Xanadu Cloud."


def version():
    """Displays the version of the Xanadu Cloud Client."""
    return f"Xanadu Cloud Client version {__version__}"


def main() -> None:
    """Entry point for the Xanadu Cloud CLI."""
    # Don't use a pager for displaying help information. For more details, see
    # https://github.com/google/python-fire/issues/188.
    fire.core.Display = lambda lines, out: print(*lines, file=out)

    try:
        fire.Fire(
            {
                "config": {
                    "get": get_setting,
                    "list": list_settings,
                    "set": set_setting,
                },
                "device": {
                    "get": get_device,
                    "list": list_devices,
                },
                "job": {
                    "get": get_job,
                    "list": list_jobs,
                    "submit": submit_job,
                },
                "ping": ping,
                "version": version,
            }
        )

    # pylint: disable=broad-except
    except Exception as exc:
        # Some exceptions, like NotImplementedError, don't have a message.
        err = str(exc).rstrip(".") or exc.__class__.__name__
        msg = Error("ERROR: ") + err + "."
        print(msg, file=sys.stderr)