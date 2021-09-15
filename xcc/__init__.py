"""
This package implements the Python API to the Xanadu Cloud (XC). Specifically,
the :class:`~xcc.Connection` class encapsulates the sending of HTTP requests to
the Xanadu Cloud while the :class:`~xcc.Device` and :class:`~xcc.Job` classes
provide interfaces for managing devices and jobs, respectively.
"""

from ._version import __version__
from .connection import Connection
from .device import Device
from .job import Job
from .settings import Settings

__all__ = ["Connection", "Device", "Job", "Settings"]
