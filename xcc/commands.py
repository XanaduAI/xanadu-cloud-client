"""
This module implements the Xanadu Cloud CLI.
"""

import functools
import json
import sys
from typing import Any, Callable, Mapping, Sequence, Tuple, Union

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
            return json.dumps(output, indent=4, default=str)
        return output

    return beautify_


def load_connection() -> Connection:
    """Loads a connection using the :class:`xcc.Settings` class.

    Returns:
        Connection: connection initialized from the configuration of a new
        :class:`xcc.Settings` instance
    """
    settings = Settings()
    return Connection(
        refresh_token=settings.REFRESH_TOKEN,
        access_token=settings.ACCESS_TOKEN,
        host=settings.HOST,
        port=settings.PORT,
        tls=settings.TLS,
        headers={"User-Agent": f"XCC/{__version__} (CLI)"},
    )


# Settings CLI
# ------------------------------------------------------------------------------


@beautify
def get_setting(name: str) -> Any:
    """Gets the value of a setting.

    Args:
        name (str): Name of the setting (e.g., "PORT").

    Returns:
        Any: Value of the setting.
    """
    key, val = _resolve_setting(name)

    if val is None:
        raise ValueError(f"The {key} setting does not currently have a value.")

    return val


@beautify
def list_settings() -> Mapping[str, Any]:
    """Lists the current settings.

    Returns:
        Mapping[str, Any]: Mapping from setting names to values.
    """
    return Settings().dict()


@beautify
def set_setting(name: str, value: Union[str, int, bool]) -> str:
    """Sets the value of a setting.

    Args:
        name (str): Name of the setting (e.g., "PORT").
        value (str, int, bool): Value of the setting (e.g., 443).

    Returns:
        str: Message indicating the setting was successfully updated.
    """
    key, _ = _resolve_setting(name)

    try:
        settings = Settings(**{key: value})
        settings.save()
    except ValidationError as exc:
        err = exc.errors()[0].get("msg", "invalid value")
        raise ValueError(f"Failed to update {key} setting: {err}") from exc

    # Using repr() ensures that strings are quoted.
    val = repr(settings.dict()[key])
    return f"Successfully updated {key} setting to {val}."


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
    availability: bool = False,
    certificate: bool = False,
    specification: bool = False,
    status: bool = False,
) -> Union[str, Mapping]:
    """Gets information about a device on the Xanadu Cloud.

    If no device property flags are specified, an overview of the device is
    displayed. Otherwise, only the selected device property is shown.

    Args:
        target (str): Name of the device target.
        availability (bool): Show the expected uptime of the device.
        certificate (bool): Show the certificate of the device.
        specification (bool): Show the specification of the device.
        status (bool): Show the status of the device.

    Returns:
        Union[str, Mapping]: Device overview or the selected device property.
    """
    device = Device(target=target, connection=load_connection())

    flags = sum(map(int, (availability, certificate, specification, status)))
    if flags > 1:
        raise FireError("At most one device property can be selected.")

    if availability:
        return device.expected_uptime
    if certificate:
        return device.certificate
    if specification:
        return device.specification
    if status:
        return device.status

    return device.overview


@beautify
def list_devices(status: str = None) -> Sequence[Mapping]:
    """Lists devices on the Xanadu Cloud.

    Args:
        status (str): Filter devices by status (e.g., "offline" or "online").

    Returns:
        Sequence[Mapping]: Overview of each device on the Xanadu Cloud.
    """
    devices = Device.list(connection=load_connection(), status=status)
    return [device.overview for device in devices]


# Job CLI
# ------------------------------------------------------------------------------


@beautify
# pylint: disable=invalid-name,redefined-builtin
def cancel_job(id: str) -> str:
    """Cancels a job on the Xanadu Cloud.

    Args:
        id (str): ID of the job.

    Returns:
        str: Message indicating the job was successfully cancelled.
    """
    job = Job(id_=id, connection=load_connection())
    job.cancel()

    if job.status not in ("cancel_pending", "cancelled"):
        raise ValueError(f"Job with ID '{id}' was not cancelled in time.")

    return f"Successfully cancelled job with ID '{id}'."


@beautify
# pylint: disable=invalid-name,redefined-builtin
def get_job(
    id: str, circuit: bool = False, result: bool = False, status: bool = False
) -> Union[str, Mapping]:
    """Gets information about a job on the Xanadu Cloud.

    If no job property flags are specified, an overview of the job is
    displayed. Otherwise, only the selected job property is shown.

    Args:
        id (str): ID of the job.
        circuit (bool): Show the circuit of the job.
        result (bool): Show the result of the job.
        status (bool): Show the status of the job.

    Returns:
        Union[str, Mapping]: Job overview or the selected job property.
    """
    job = Job(id_=id, connection=load_connection())

    flags = sum(map(int, (circuit, result, status)))
    if flags > 1:
        raise FireError("At most one job property can be selected.")

    if circuit:
        return job.circuit
    if status:
        return job.status
    if result:
        return job.result

    return job.overview


@beautify
def list_jobs(limit: int = 10) -> Sequence[Mapping]:
    """Lists jobs submitted to the Xanadu Cloud.

    Args:
        limit (int): Maximum number of jobs to display.

    Returns:
        Sequence[Mapping]: Overview of each job submitted to the Xanadu Cloud.
    """
    jobs = Job.list(connection=load_connection(), limit=limit)
    return [job.overview for job in jobs]


@beautify
def submit_job(name: str, target: str, circuit: str, language: str = "blackbird:1.0") -> Mapping:
    """Submits a job to the Xanadu Cloud.

    Args:
        name (str): Name of the job.
        target (str): Target of the job.
        circuit (str): Circuit of the job.
        language (str): Language of the job.

    Returns:
        Mapping: Overview of the submitted job.
    """
    job = Job.submit(
        connection=load_connection(),
        name=name,
        target=target,
        circuit=circuit.replace("\\n", "\n"),
        language=language,
    )
    return job.overview


# Other CLI
# ------------------------------------------------------------------------------


def ping() -> str:
    """Tests the connection to the Xanadu Cloud.

    Returns:
        str: Message indicating the ping was successful.
    """
    connection = load_connection()
    connection.ping()
    return "Successfully connected to the Xanadu Cloud."


def version() -> str:
    """Displays the version of the Xanadu Cloud Client.

    Returns:
        str: Message with the version of this Python package.
    """
    return f"Xanadu Cloud Client version {__version__}"


def main() -> None:
    """Entry point for the Xanadu Cloud CLI."""
    # Using a pager to display help information can be annoying since it hides
    # the output (and possible error messages) of previous commands. To remedy
    # this, the assignment below replaces the pager with the print() function.
    # See https://github.com/google/python-fire/issues/188 for more details.
    fire.core.Display = lambda lines, out: print(
        *lines, file=out
    )  # pyright: reportGeneralTypeIssues=false

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
                    "cancel": cancel_job,
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
