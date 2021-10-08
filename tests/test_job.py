# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.job` module.
"""

import io
import json
from datetime import datetime, timedelta
from typing import Callable
from unittest.mock import call, patch

import dateutil.parser
import numpy as np
import numpy.lib.npyio
import pytest
import responses

import xcc


@pytest.fixture
def job_id() -> str:
    """Returns a mock job ID."""
    return "00000000-0000-0000-0000-000000000000"


@pytest.fixture
def job(job_id, connection) -> xcc.Job:
    """Returns a mock job with the given connection."""
    return xcc.Job(job_id, connection)


@pytest.fixture
def datetime_() -> datetime:
    """Returns a mock datetime."""
    return dateutil.parser.isoparse("2020-01-03T12:34:56.789012Z")


@pytest.fixture
def add_response(job_id, connection) -> Callable[[object, str], None]:
    """Returns a function that places a JSON serialization of its argument
    inside the body of an HTTP 200 response to the next GET request to the
    specified path ("/jobs/<job_id>" by default) using the given connection.
    """

    def add_response_(body: object, path: str = f"/jobs/{job_id}") -> None:
        url = connection.url(path)
        responses.add(responses.GET, url, status=200, body=json.dumps(body))

    return add_response_


class TestJob:
    """Tests the :class:`xcc.Job` class."""

    @pytest.mark.parametrize(
        "limit, want_names",
        [
            (1, ["foo"]),
            (2, ["foo", "bar"]),
        ],
    )
    @responses.activate
    def test_list(self, connection, add_response, limit, want_names):
        """Tests that the correct jobs are listed."""
        data = [
            {
                "id": "00000000-0000-0000-0000-000000000001",
                "name": "foo",
                "status": "queued",
                "target": "qpu",
                "created_at": "2020-01-03T12:34:56.789012+00:00",
            },
            {
                "id": "00000000-0000-0000-0000-000000000002",
                "name": "bar",
                "status": "complete",
                "target": "qpu",
                "created_at": "2020-01-03T12:34:56.789012+00:00",
                "finished_at": "2020-01-03T12:34:56.789013+00:00",
            },
        ][:limit]
        add_response(body={"data": data}, path="/jobs")

        have_names = [job.name for job in xcc.Job.list(connection, limit=limit)]
        assert have_names == want_names

        have_params = responses.calls[0].request.params  # pyright: reportGeneralTypeIssues=false
        want_params = {"size": str(limit)}
        assert have_params == want_params

    @responses.activate
    def test_submit(self, job_id, connection):
        """Tests that a job can be submitted."""
        details = json.dumps({"id": job_id, "name": "foo"})
        responses.add(responses.POST, connection.url("/jobs"), status=200, body=details)

        job = xcc.Job.submit(connection, name="foo", target="bar", circuit="baz", language="qux")
        assert job.id == job_id
        assert job.name == "foo"

    def test_id(self, job):
        """Tests that the correct ID is returned for a job."""
        assert job.id == "00000000-0000-0000-0000-000000000000"

    @responses.activate
    def test_overview(self, job, add_response, datetime_):
        """Tests that the correct overview is returned for a job."""
        body = {
            "id": job.id,
            "name": "foo",
            "status": "complete",
            "target": "bar",
            "language": "baz",
            "created_at": datetime_.isoformat(),
            "finished_at": datetime_.isoformat(),
            "running_time": 0.12345,
        }
        add_response(body=body)
        assert set(job.overview) == set(body)

    @responses.activate
    def test_result_npy(self, connection, job):
        """Tests that the correct .npy result is returned for a job."""
        result = np.array([[0, 1, 2, 3], [4, 5, 6, 7]], dtype=np.int64)

        with io.BytesIO() as buffer:
            np.save(file=buffer, arr=result, allow_pickle=False)

            buffer.seek(0)
            body = buffer.read()

            path = f"/jobs/{job.id}/result"
            responses.add(responses.GET, connection.url(path), status=200, body=body)

            assert job.result == pytest.approx(result)

    @responses.activate
    def test_result_npz(self, connection, job):
        """Tests that the correct .npz result is returned for a job."""
        result = [np.complex64(1 + 2j), np.arange(5)]

        with io.BytesIO() as buffer:
            # The public savez() function does not allow pickling to be disabled.
            savez = numpy.lib.npyio._savez  # pylint: disable=protected-access
            savez(file=buffer, args=result, kwds={}, compress=False, allow_pickle=False)

            buffer.seek(0)
            body = buffer.read()

            path = f"/jobs/{job.id}/result"
            responses.add(responses.GET, connection.url(path), status=200, body=body)

            assert len(job.result) == len(result)
            assert [have == pytest.approx(want) for have, want in zip(job.result, result)]

    @responses.activate
    def test_created_at(self, job, add_response, datetime_):
        """Tests that the correct creation time is returned for a job."""
        add_response(body={"started_at": datetime_.isoformat()})
        assert job.started_at == datetime_

    @responses.activate
    def test_started_at_of_unstarted_job(self, job, add_response):
        """Tests that the correct start time is returned for an unstarted job."""
        add_response(body={"started_at": None})
        assert job.started_at is None

    @responses.activate
    def test_started_at_of_started_job(self, job, datetime_, add_response):
        """Tests that the correct start time is returned for a started job."""
        add_response(body={"started_at": datetime_.isoformat()})
        assert job.started_at == datetime_

    @responses.activate
    def test_finished_at_of_unfinished_job(self, job, add_response):
        """Tests that the correct finish time is returned for an unfinished job."""
        add_response(body={"finished_at": None})
        assert job.finished_at is None

    @responses.activate
    def test_finished_at_of_finished_job(self, job, datetime_, add_response):
        """Tests that the correct finish time is returned for a finished job."""
        add_response(body={"finished_at": datetime_.isoformat()})
        assert job.finished_at == datetime_

    @responses.activate
    def test_running_time_of_finished_job(self, job, add_response):
        """Tests that the correct running time is returned for an unfinished job."""
        add_response(body={"running_time": None})
        assert job.running_time is None

    @responses.activate
    def test_running_time_of_unfinished_job(self, job, add_response):
        """Tests that the correct running time is returned for a finished job."""
        add_response(body={"running_time": 12.34})
        assert job.running_time == timedelta(seconds=12.34)

    @responses.activate
    def test_circuit(self, job, add_response):
        """Tests that the correct circuit is returned for a job."""
        add_response(body={"circuit": "foo"}, path=f"/jobs/{job.id}/circuit")
        assert job.circuit == "foo"

    @responses.activate
    def test_language(self, job, add_response):
        """Tests that the correct language is returned for a job."""
        add_response(body={"language": "foo"})
        assert job.language == "foo"

    @responses.activate
    def test_name(self, job, add_response):
        """Tests that the correct name is returned for a job."""
        add_response(body={"name": "foo"})
        assert job.name == "foo"

    @responses.activate
    def test_target(self, job, add_response):
        """Tests that the correct target is returned for a job."""
        add_response(body={"target": "foo"})
        assert job.target == "foo"

    @responses.activate
    def test_status(self, job, add_response):
        """Tests that the correct status is returned for a job."""
        add_response(body={"status": "complete"})
        assert job.status == "complete"

    @pytest.mark.parametrize(
        "status, finished",
        [
            ("open", False),
            ("queued", False),
            ("cancelled", True),
            ("failed", True),
            ("cancel_pending", False),
            ("complete", True),
        ],
    )
    @responses.activate
    def test_finished(self, job, add_response, status, finished):
        """Tests that the correct finished indicator is returned for a job."""
        add_response(body={"status": status})
        assert job.finished is finished

    def test_repr(self, job):
        """Tests that the correct printable representation is returned for a job."""
        assert repr(job) == f"<Job: id={job.id}>"

    @responses.activate
    def test_cancel(self, connection, job, add_response):
        """Tests that a job can be cancelled."""
        add_response(body={"status": "open"})
        add_response(body={"status": "cancelled"})

        url = connection.url(f"/jobs/{job.id}")
        responses.add(responses.PATCH, url, status=204)

        assert job.finished is False
        assert len(responses.calls) == 1

        job.cancel()
        assert len(responses.calls) == 2

        assert job.finished is True
        assert len(responses.calls) == 3

    @responses.activate
    def test_clear(self, job, add_response):
        """Tests that the cache of a job can be cleared."""
        add_response(body={"status": "queued"})
        add_response(body={"status": "complete"})

        assert job.status == "queued"
        assert len(responses.calls) == 1

        job.clear()
        assert len(responses.calls) == 1

        assert job.status == "complete"
        assert len(responses.calls) == 2

    @responses.activate
    def test_cache_independence(self, connection, job_id, add_response):
        """Tests that caches are not shared across job instances."""
        add_response(body={"status": "open"})
        add_response(body={"status": "queued"})
        add_response(body={"status": "complete"})
        add_response(body={"status": "complete"})

        job_1 = xcc.Job(job_id, connection)
        job_2 = xcc.Job(job_id, connection)

        assert job_1.status == "open"
        assert job_2.status == "queued"

        job_1.clear()

        assert job_1.status == "complete"
        assert job_2.status == "queued"

        job_2.clear()

        assert job_1.status == "complete"
        assert job_2.status == "complete"

    @patch("xcc.job.time.sleep")
    @responses.activate
    def test_wait_on_unfinished_job(self, sleep, job, add_response):
        """Tests that waiting on an unfinished job triggers the correct number
        of polling cycles and that each polling cycle has the correct latency.
        """
        add_response(body={"status": "open"})
        add_response(body={"status": "queued"})
        add_response(body={"status": "complete"})

        job.wait(delay=0.123)
        sleep.assert_has_calls([call(0.123), call(0.123)])

        assert len(responses.calls) == 3
        assert job.finished

    @patch("xcc.job.time.sleep")
    @responses.activate
    def test_wait_on_finished_job(self, sleep, job, add_response):
        """Tests that waiting on a finished job does not trigger a polling
        cycle or send any HTTP requests to the Xanadu Cloud.
        """
        add_response(body={"status": "complete"})

        job.wait(delay=1)
        sleep.assert_not_called()

        assert len(responses.calls) == 1
        assert job.finished
