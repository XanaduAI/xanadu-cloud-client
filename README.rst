.. image:: https://raw.githubusercontent.com/XanaduAI/xanadu-cloud-client/main/docs/_static/xcc_title.svg
    :alt: XCC
    :height: 65
    :width: 100%

The `Xanadu Cloud Client <https://xanadu-cloud-client.readthedocs.io>`_ (XCC) is
a Python API and CLI for the Xanadu Cloud.

.. inclusion-marker-for-features-start

Features
--------

* *Simple*. Easy to setup, explore, and use.

* *Efficient*. Lazy fetching and caching by default.

* *Structured*. Parse Xanadu Cloud responses into JSON or Python objects.

.. inclusion-marker-for-features-end
.. inclusion-marker-for-installation-start

Installation
-------------

The XCC requires Python version 3.7 or above. Installation of the XCC, as well
as all dependencies, can be done using pip:

.. code-block:: console

    pip install xanadu-cloud-client

.. inclusion-marker-for-installation-end
.. inclusion-marker-for-setup-start

Setup
-----

To use the XCC, a Xanadu Cloud API key (or equivalent JWT refresh token) is
required. There are several ways to register your API key with the XCC:

1.  Save your API key to the XCC configuration file using the CLI:

    .. code-block:: console

        xcc config set REFRESH_TOKEN "Xanadu Cloud API key goes here"

2.  Set the ``XANADU_CLOUD_REFRESH_TOKEN`` environment variable:

    .. code-block:: console

        export XANADU_CLOUD_REFRESH_TOKEN="Xanadu Cloud API key goes here"

3.  Save your API key to the XCC configuration file using the Python API:

    .. code-block:: python

        import xcc

        settings = xcc.Settings(REFRESH_TOKEN="Xanadu Cloud API key goes here")
        settings.save()

Afterwards, you can verify that your API key was set correctly using either:

1.  The CLI:

    .. code-block:: console

        $ xcc ping
        Successfully connected to the Xanadu Cloud.

2.  The Python API:

    .. code-block:: console

        import xcc

        connection = xcc.commands.load_connection()
        assert connection.ping().ok

.. inclusion-marker-for-setup-end
.. inclusion-marker-for-tutorial-start

Tutorial
--------

The following tutorial illustrates a workflow for submitting a job to the Xanadu
Cloud using the CLI. For more detailed usage instructions, use ``--help`` or
refer to the Python API documentation.

1.  Before submitting a job, it is a good idea to check which devices are
    currently accepting jobs on the Xanadu Cloud:

    .. code-block:: console

        $ xcc device list --status online

    .. code-block:: json

        [
            {
                "target": "simulon_gaussian",
                "status": "online"
            },
            {
                "target": "X8_01",
                "status": "online"
            }
        ]

2.  Suppose that the ``simulon_gaussian`` device is of interest. The capabilities,
    operating conditions, and other properties of a device can be queried by
    supplying the appropriate flag to the `xcc device get` command:

    .. code-block:: console

        $ xcc device get simulon_gaussian --availability

    .. code-block:: json

        {
            "monday": [
                "00:00:00+00:00",
                "23:59:59+00:00"
            ],
            "tuesday": [
                "00:00:00+00:00",
                "23:59:59+00:00"
            ],
            "wednesday": [
                "00:00:00+00:00",
                "23:59:59+00:00"
            ],
            "thursday": [
                "00:00:00+00:00",
                "23:59:59+00:00"
            ],
            "friday": [
                "00:00:00+00:00",
                "23:59:59+00:00"
            ],
            "saturday": [
                "00:00:00+00:00",
                "23:59:59+00:00"
            ],
            "sunday": [
                "00:00:00+00:00",
                "23:59:59+00:00"
            ]
        }

    **Note:** Given that ``simulon_gaussian`` is a simulator, it does not have
    any scheduled downtime for maintenance.

3.  Now, consider a Blackbird script stored in a local file named ``circuit.xbb``:

    .. code-block:: console

        $ cat circuit.xbb
        name example
        version 1.0
        target simulon_gaussian (shots=4)

        MeasureFock() | [0, 1, 2]

    This circuit can be submitted to the ``simulon_gaussian`` device using the
    ``xcc job submit`` command:

    .. code-block:: console

        $ xcc job submit --name example \
            --target simulon_gaussian \
            --language "blackbird:1.0" \
            --circuit "$(cat circuit.xbb)"

    .. code-block:: json

        {
            "id": "4c043f6d-54c7-4915-bbb8-eb1b99c4d88e",
            "name": "example",
            "status": "open",
            "target": "simulon_gaussian",
            "created_at": "2021-09-24 17:52:00.532938+00:00",
            "finished_at": null,
            "running_time": null
        }

    **Note:** Replace ``cat foo.xbb`` with ``Get-Content foo.xbb -Raw`` on Windows PowerShell.

4.  The ID of a job can be used to retrieve additional information about that
    job, including its status and running time. Specifically, the ID can be
    supplied to the `xcc job get` command along with an optional flag:

    .. code-block:: console

        $ xcc job get 4c043f6d-54c7-4915-bbb8-eb1b99c4d88e --status
        complete

    The result of a job can be accessed in a similar way:

    .. code-block:: console

        $ xcc job get 4c043f6d-54c7-4915-bbb8-eb1b99c4d88e --result

    .. code-block:: json

        {
            "output": [
                "[[0 0 0]\n[0 0 0]\n[0 0 0]\n[0 0 0]]"
            ]
        }

.. inclusion-marker-for-tutorial-end

Contributions
-------------

We welcome contributions - simply fork the XCC repository and make a `pull
request <https://help.github.com/articles/about-pull-requests/>`_ containing
your contribution. All contributors to the XCC will be listed as authors on the
releases. See our `changelog <https://github.com/XanaduAI/xanadu-cloud-client/blob/main/.github/CHANGELOG.md>`_
for more details.

We also encourage bug reports, suggestions for new features and enhancements,
and even links to cool projects or applications built on top of the XCC. Visit
the `contributions page <https://github.com/XanaduAI/xanadu-cloud-client/blob/main/.github/CONTRIBUTING.md>`_
to learn more about sharing your ideas with the XCC team.

Support
-------

- **Source Code:** https://github.com/XanaduAI/xanadu-cloud-client
- **Issue Tracker:** https://github.com/XanaduAI/xanadu-cloud-client/issues

If you are having issues, please let us know by posting the issue on our GitHub
issue tracker.

Authors
-------

The XCC is the work of `many contributors
<https://github.com/XanaduAI/xir/graphs/contributors>`_.

.. inclusion-marker-for-license-start

License
--------

The XCC is **free** and **open source**, released under the `Apache License,
Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_.

.. inclusion-marker-for-license-end
