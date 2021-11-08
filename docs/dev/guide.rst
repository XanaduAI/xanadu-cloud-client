Development guide
=================

.. _dependencies:

Dependencies
------------

The XCC requires the following libraries be installed:

* `Python <http://python.org/>`_ >= 3.7

as well as the following Python packages:

* `appdirs <https://pypi.org/project/appdirs/>`_
* `dateutil <https://dateutil.readthedocs.io/>`_
* `NumPy <http://numpy.org/>`_
* `pydantic[dotenv] <https://pydantic-docs.helpmanual.io/>`_
* `Python Fire <https://github.com/google/python-fire>`_
* `Requests <https://docs.python-requests.org/en/latest/>`_


Installation
------------

For development purposes, it is recommended to install the XCC source code using
development mode:

.. code-block:: bash

    git clone https://github.com/XanaduAI/xanadu-cloud-client
    cd xanadu-cloud-client
    pip install -e .

The ``-e`` flag ensures that edits to the source code will be reflected when
importing the XCC in Python.

Additional dependencies for linting, formatting, and testing can be installed using:

.. code-block:: bash

    pip install -r requirements-dev.txt

.. _test-section:

Tests
-----

To ensure that the XCC is working correctly after installation, the test suite
can be run by navigating to the source code folder and running

.. code-block:: bash

    make test

while the test coverage can be checked by running

.. code-block:: bash

    make coverage

The output of the first command should resemble

.. code-block:: text

    ======================================= test session starts ========================================
    platform linux -- Python 3.9.6, pytest-6.2.5, py-1.10.0, pluggy-1.0.0
    rootdir: /path/to/xanadu-cloud-client
    plugins: cov-3.0.0
    collected 109 items

    tests/test_commands.py ..............................                                        [ 27%]
    tests/test_connection.py ...........................                                         [ 52%]
    tests/test_device.py ...............                                                         [ 66%]
    tests/test_job.py ...............................                                            [ 94%]
    tests/test_settings.py ......                                                                [100%]

    ======================================= 109 passed in 0.59s ========================================

Format
------

Contributions are checked for format alignment in the pipeline. Changes can be
formatted and linted locally using:

.. code-block:: bash

    make format lint

Documentation
-------------

Additional packages are required to build the documentation, as specified in
``docs/requirements.txt``. These packages can be installed using

.. code-block:: bash

    pip install -r docs/requirements.txt

To then build the HTML documentation, run

.. code-block:: bash

    make docs

The documentation can be found in the :file:`docs/_build/html/` directory.

Submitting a pull request
-------------------------

Before submitting a pull request, please make sure the following is done:

* **All new features must include a unit test.** If you've fixed a bug or added
  code that should be tested, add a test to the ``tests/`` directory.

* **All new functions and code must be clearly commented and documented.**

  Have a look through the source code at some of the existing functions ---
  the easiest approach is to simply copy an existing docstring and modify it as
  appropriate.

  If you do make documentation changes, make sure that the docs build and render
  correctly by running ``make docs``.

* **Ensure that the test suite passes**, by following the :ref:`test suite guide<test-section>`.

* **Make sure the modified code in the pull request conforms to the PEP8 coding standard.**

  The XCC source code conforms to
  `PEP8 standards <https://www.python.org/dev/peps/pep-0008/>`_. Before
  submitting the PR, you can autoformat your code changes using the
  `Black <https://github.com/psf/black>`_ Python autoformatter, with max-line
  length set to 100:

  .. code-block:: bash

      black -l 100 xanadu-cloud-client/path/to/modified/file.py

  We check all of our code against `Pylint <https://www.pylint.org/>`_ for
  errors. To lint modified files, simply ``pip install pylint``, and then from
  the source code directory, run

  .. code-block:: bash

      pylint xanadu-cloud-client/path/to/modified/file.py

When ready, submit your fork as a `pull request <https://help.github.com/articles/about-pull-requests>`_
to the XCC repository, filling out the pull request template. This template is
added automatically to the comment box when you create a new issue.

* When describing the pull request, please include as much detail as possible
  regarding the changes made/new features added/performance improvements. If
  including any bug fixes, mention the issue numbers associated with the bugs.

* Once you have submitted the pull request, the **test suite** will
  automatically run on GitHub Actions to ensure that all tests continue to pass.
