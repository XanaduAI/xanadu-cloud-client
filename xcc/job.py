"""
This module contains the :class:`~xcc.Job` class.
"""

from __future__ import annotations

import io
import time
from datetime import datetime, timedelta
from typing import Any, List, Mapping, Optional, Sequence, Union
from urllib.parse import urlparse

import numpy as np

from .connection import Connection
from .util import cached_property


class Job:
    """Represents a job on the Xanadu Cloud.

    Args:
        id_ (str): ID of the job
        connection (Connection): connection to the Xanadu Cloud

    .. note::

        For performance reasons, the properties of a job are lazily fetched and
        stored in a cache. This cache can be cleared at any time by calling
        :meth:`Job.clear`.

    .. warning::

        The :class:`xcc.Job` class transparently contacts the Xanadu Cloud when
        an uncached job property is accessed. This means that requesting a job
        property for the first time may take longer than expected.

    **Example:**

    The following example shows how to use the :class:`Job` class to submit and
    track a job for a simulator on the Xanadu Cloud. First, a connection is
    established to the Xanadu Cloud:

    >>> import xcc
    >>> connection = xcc.Connection(key="Xanadu Cloud API key goes here")

    Next, the parameters of the desired job are prepared. At present, this
    includes the name, target, circuit, and language of the job:

    >>> import inspect
    >>> name = "example"
    >>> target = "simulon_gaussian"
    >>> circuit = inspect.cleandoc(
            f\"\"\"
            name {name}
            version 1.0
            target {target} (shots=3)

            MeasureFock() | [0, 1, 2, 3];
            \"\"\"
        )
    >>> language = "blackbird:1.0"

    The job is then submitted to the Xanadu Cloud using the :func:`Job.submit`
    function:

    >>> job = xcc.Job.submit(
            connection,
            name=name,
            target=target,
            circuit=circuit,
            language=language,
        )

    At this point, the Xanadu Cloud has received the job; however, it may take
    some time before the result of the job is available. To wait until the job
    is finished, a blocking call is made to :meth:`Job.wait`:

    >>> job.wait()

    Finally, the status, result, running time, etc. of the job are retrieved by
    accessing the corresponding properties of the job:

    >>> job.status
    'completed'
    >>> job.result
    array([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0]], dtype=uint64)
    >>> job.running_time
    0.123456
    """

    @staticmethod
    def list(connection: Connection, status: Optional[str] = None, limit: int = 5) -> Sequence[Job]:
        """Returns jobs submitted to the Xanadu Cloud.

        Args:
            connection (Connection): connection to the Xanadu Cloud
            status (str, optional): optionally filter jobs by status
            limit (int): maximum number of jobs to retrieve

        Returns:
            Sequence[Job]: jobs on the Xanadu Cloud which match the status
            filter and were submitted by the user associated with the Xanadu
            Cloud connection
        """
        response = connection.request("GET", "/jobs", params={"size": limit})

        def include(details: Mapping[str, Any]) -> bool:
            """Returns ``True`` if a job with the given details should be
            included in the response.  Otherwise, ``False`` is returned.
            """
            return status is None or details["status"] == status

        jobs = []

        for details in filter(include, response.json()["data"]):
            job = Job(details["id"], connection=connection)
            job._details = details  # pylint: disable=protected-access
            jobs.append(job)

        return jobs

    @staticmethod
    def submit(connection: Connection, name: str, target: str, circuit: str, language: str) -> Job:
        """Submits a job to the Xanadu Cloud.

        Args:
            connection (Connection): connection to the Xanadu Cloud
            name (str): name of the job
            target (str): target of the job
            circuit (str): circuit of the job
            language (str): language of the job

        Returns:
            Job: job submitted to the Xanadu Cloud
        """
        payload = {"name": name, "target": target, "circuit": circuit, "language": language}
        response = connection.request("POST", "/jobs", json=payload)
        details = response.json()

        job = Job(details["id"], connection=connection)

        # pylint: disable=protected-access
        job._details = details
        job._circuit = {"circuit": circuit, "language": language}

        return job

    def __init__(self, id_: str, connection: Connection) -> None:
        self._id = id_
        self._connection = connection

    @property
    def connection(self) -> Connection:
        """Returns the connection used to access the Xanadu Cloud."""
        return self._connection

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """Returns the ID of a job."""
        return self._id

    @property
    def overview(self) -> Mapping[str, Any]:
        """Returns an overview of a job.

        Returns:
            Mapping[str, Any]: mapping from field names to values for this job
            as determined by the needs of a Xanadu Cloud user.
        """
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "target": self.target,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "running_time": self.running_time,
        }

    @cached_property
    def result(self) -> Union[np.ndarray, List[Union[np.number, np.ndarray]]]:
        """Returns the result of a job.

        Returns:
            Union[np.ndarray, List[Union[np.number, np.ndarray]]]: result of
            this job
        """
        url = self._details["result_url"]
        path = urlparse(url).path
        response = self.connection.request("GET", path)

        # Adapted from strawberryfields.api.Connection.get_job_result().
        # The result of a job on the Xanadu Cloud is an HTTP response with a
        # payload containing the bytes of either an .npy or .npz file depending
        # on the language of the submitted job.
        with io.BytesIO(response.content) as buffer:
            result = np.load(buffer, allow_pickle=False)

            if not isinstance(result, np.ndarray):
                # The payload is a .npz file.
                result = [result[fname] for fname in result.files]

            elif np.issubdtype(result.dtype, np.integer):
                # The payload is a .npy file with integral entries.
                result = result.astype(np.int64)

            return result

    @property
    def created_at(self) -> datetime:
        """Returns when a job was created.

        Returns:
            datetime: datetime when this job was created
        """
        return datetime.fromisoformat(self._details["created_at"])

    @property
    def started_at(self) -> Optional[datetime]:
        """Returns when a job started.

        Returns:
            datetime, optional: datetime when this job started
        """
        datetime_ = self._details["started_at"]
        return None if datetime_ is None else datetime.fromisoformat(datetime_)

    @property
    def finished_at(self) -> Optional[datetime]:
        """Returns when a job finished.

        Returns:
            datetime, optional: datetime when this job finished
        """
        datetime_ = self._details["finished_at"]
        return None if datetime_ is None else datetime.fromisoformat(datetime_)

    @property
    def running_time(self) -> Optional[timedelta]:
        """Returns the running time of a job.

        Returns:
            timedelta, optional: running time of this job
        """
        seconds = self._details["running_time"]
        return None if seconds is None else timedelta(seconds=seconds)

    @property
    def circuit(self) -> str:
        """Returns the circuit of a job.

        Returns:
            str: circuit of this job
        """
        return self._circuit["circuit"]

    @property
    def language(self) -> str:
        """Returns the language of a job.

        Returns:
            str: language of this job
        """
        return self._circuit["language"]

    @property
    def name(self) -> str:
        """Returns the name of a job.

        Returns:
            str: name of this job
        """
        return self._details["name"]

    @property
    def target(self) -> str:
        """Returns the target of a job.

        Returns:
            str: target of this job
        """
        return self._details["target"]

    @property
    def status(self) -> str:
        """Returns the current status of a job.

        Returns:
            str: status of this job ("open", "queued", "cancelled", "failed",
            "cancel_pending", or "completed")
        """
        return self._details["status"]

    @property
    def finished(self) -> bool:
        """Returns whether this job has finished.

        Returns:
            bool: ``True`` iff the job status is "cancelled", "completed", or
            "failed"
        """
        return self.status in ("cancelled", "completed", "failed")

    @cached_property
    def _details(self) -> Mapping[str, Any]:
        """Returns the details of a job.

        Returns:
            Mapping[str, Any]: mapping from field names to values for this job
                as determined by the Xanadu Cloud job endpoint.

        .. note::

            These fields are not intended to be directly accessed by external
            callers. Instead, they should be individually retrieved through
            their associated public properties.
        """
        return self.connection.request("GET", f"/jobs/{self.id}").json()

    @cached_property
    def _circuit(self) -> Mapping[str, str]:
        """Returns the circuit and language of a job.

        Returns:
            Mapping[str, str]: mapping with "circuit" and "language" fields

        .. note::

            The circuit and language should be retrieved through the
            :attr:`Device.circuit` and :attr:`Device.language` properties,
            respectively.
        """
        url = self._details["circuit_url"]
        path = urlparse(url).path
        return self.connection.request("GET", path).json()

    def __repr__(self) -> str:
        """Returns a printable representation of a job."""
        return f"<{self.__class__.__name__}: id={self.id}>"

    def cancel(self) -> None:
        """Cancels a job."""
        if not self.finished:
            self.connection.request("PATCH", f"/jobs/{self.id}", json={"status": "cancelled"})
            self.clear()

    def clear(self) -> None:
        """Clears the details, circuit, and result caches of a job."""
        del self._details
        del self._circuit
        del self.result

    def wait(self, delay: float = 1) -> None:
        """Waits for a job to finish.

        Args:
            delay (float): number of seconds to wait between polling requests
        """
        while not self.finished:
            time.sleep(delay)
            self.clear()
