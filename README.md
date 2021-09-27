<p align="center">
  <img height=65 alt="XCC" src="docs/_static/xcc_title.svg">
</p>

<p align="center">
  The <b>Xanadu Cloud Client</b> (XCC) is a Python API and CLI for the Xanadu Cloud.
</p>

## Features

- *Simple*. Easy to setup, explore, and use.

- *Efficient*. Lazy fetching and caching by default.

- *Structured*. Parse Xanadu Cloud responses into JSON or Python objects.

## Installation

The XCC requires Python version 3.7 or above. Installation of the XCC, as well
as all dependencies, can be done using pip:

```console
pip install git+https://github.com/XanaduAI/xanadu-cloud-client#egg=xanadu-cloud-client
```

## Setup

To use the XCC, a Xanadu Cloud API key is required. There are several ways to
register your API key with the XCC:

1. Save your API key to the XCC configuration file using the CLI:
    ```console
    xcc config set API_KEY "Xanadu Cloud API key goes here"
    ```

2. Set the `XANADU_CLOUD_API_KEY` environment variable:
    ```console
    export XANADU_CLOUD_API_KEY="Xanadu Cloud API key goes here"
    ```

3. Save your API key to the XCC configuration file using the Python API:
    ```python
    import xcc

    settings = xcc.Settings(API_KEY="Xanadu Cloud API key goes here")
    settings.save()
    ```

Afterwards, you can verify that your API key was set correctly using the CLI or Python API:

1. Using the CLI:
    ```console
    $ xcc ping
    Successfully connected to the Xanadu Cloud.
    ```

2. Using the Python API:
    ```python
    import xcc

    connection = xcc.commands.load_connection()
    assert connection.ping().ok
    ```

## Tutorial

The following tutorial illustrates a workflow for submitting a job to the Xanadu
Cloud using the CLI. For more detailed usage instructions, use `--help` or refer
to the Python API documentation.

1.  Before submitting a job, it is a good idea to check which devices are
    currently accepting jobs on the Xanadu Cloud:

    ```console
    $ xcc device list --status online
    ```
    ```json
    [
        {
            "target": "simulon_gaussian",
            "status": "online"
        },
        {
            "target": "simulon_jet",
            "status": "online"
        },
        {
            "target": "X8_01",
            "status": "online"
        }
    ]
    ```

2.  Suppose that the `simulon_gaussian` device is of interest. The capabilities,
    operating conditions, and other properties of a device can be queried by
    supplying the appropriate flag to the `xcc device get` command:

    ```console
    $ xcc device get X8_01 --availability
    ```
    ```json
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
    ```

    **Note:** Given that `simulon_gaussian` is a simulator, it does not have
    any scheduled downtime for maintenance.

3.  Now, consider a Blackbird script stored in a local file named `circuit.xbb`:

    ```console
    $ cat circuit.xbb
    name example
    version 1.0
    target simulon_gaussian (shots=4)

    MeasureFock() | [0, 1, 2]
    ```

    This circuit can be submitted to the `simulon_gaussian` device using the
    `xcc job submit` command:

    ```console
    $ xcc job submit --name example \
        --target simulon_gaussian \
        --language "blackbird:1.0" \
        --circuit `cat circuit.xbb`
    ```
    ```json
    {
        "id": "4c043f6d-54c7-4915-bbb8-eb1b99c4d88e",
        "name": "example",
        "status": "open",
        "target": "simulon_gaussian",
        "created_at": "2021-09-24 17:52:00.532938+00:00",
        "finished_at": null,
        "running_time": null
    }
    ```

4.  The ID of a job can be used to retrieve additional information about that
    job, including its status and running time. Specifically, the ID can be
    supplied to the `xcc job get` command along with an optional flag:

    ```console
    $ xcc job get 4c043f6d-54c7-4915-bbb8-eb1b99c4d88e --status
    complete
    ```

    The result of a job can be accessed in a similar way:

    ```console
    $ xcc job get 4c043f6d-54c7-4915-bbb8-eb1b99c4d88e --result
    [[0 0 0]
     [0 0 0]
     [0 0 0]
     [0 0 0]]
    ```
## Contributions

We welcome contributions - simply fork the XCC repository and make a [pull
request](https://help.github.com/articles/about-pull-requests/) containing your
contribution. All contributors to the XCC will be listed as authors on the
releases. See our [changelog](.github/CHANGELOG.md) for more details.

We also encourage bug reports, suggestions for new features and enhancements,
and even links to cool projects or applications built on top of the XCC. Visit
the [contributions page](.github/CONTRIBUTING.md) to learn more about sharing
your ideas with the XCC team.

## Support

- **Source Code:** https://github.com/XanaduAI/xanadu-cloud-client
- **Issue Tracker:** https://github.com/XanaduAI/xanadu-cloud-client/issues

If you are having issues, please let us know by posting the issue on our GitHub
issue tracker.

## Authors

The XCC is the work of [several contributors](https://github.com/XanaduAI/xir/graphs/contributors).

## License

The XCC is **free** and **open source**, released under the
[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
