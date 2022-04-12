XCC Documentation
#################

.. rst-class:: lead grey-text ml-2

:Release: |release|

.. raw:: html

    <style>
        .breadcrumb {
            display: none;
        }
        h1 {
            text-align: center;
            margin-bottom: 15px;
        }
        p.lead.grey-text {
            margin-bottom: 30px;
        }
        .footer-relations {
            border-top: 0px;
        }
    </style>

    <div class="container mt-2 mb-2">
        <p align="center" class="lead grey-text">
            The Xanadu Cloud Client (XCC) is a Python API and CLI for the Xanadu Cloud.
        </p>
        <div class="row mt-3">

.. index-card::
    :name: Key Concepts
    :link: use/introduction.html
    :description: Learn about XCC features

.. index-card::
    :name: Getting Started
    :link: dev/guide.html
    :description: Learn how to quickly get started using the XCC

.. index-card::
    :name: API
    :link: api/xcc.html
    :description: Explore the XCC package

.. raw:: html

        </div>
    </div>

.. include:: ../README.rst
    :start-after: inclusion-marker-for-features-start
    :end-before: inclusion-marker-for-features-end

.. include:: ../README.rst
    :start-after: inclusion-marker-for-license-start
    :end-before: inclusion-marker-for-license-end

.. toctree::
   :maxdepth: 2
   :caption: Using the XCC
   :hidden:

   use/introduction
   use/walkthrough

.. toctree::
   :maxdepth: 2
   :caption: Development
   :hidden:

   dev/guide
   dev/research
   dev/releases

.. toctree::
   :maxdepth: 2
   :caption: API
   :hidden:

   api/xcc
   api/xcc.Connection
   api/xcc.Device
   api/xcc.Job
   api/xcc.Settings