XCC Documentation
#################

.. rst-class:: lead grey-text ml-2

:Release: |release|

.. raw:: html

    <style>
        #right-column.card {
            box-shadow: none!important;
        }
        #right-column.card:hover {
            box-shadow: none!important;
        }
        .breadcrumb {
            display: none;
        }
        h1 {
            text-align: center;
            margin-bottom: 15px;
        }
        .footer-relations {
            border-top: 0px;
        }
    </style>
    <div style='clear:both'></div>
    <div class="container mt-2 mb-2">
        <p align="center" class="lead grey-text">
            The Xanadu Cloud Client (XCC) is a Python API and CLI for the Xanadu Cloud.
        </p>
        <div class="row mt-3">
            <div class="col-lg-4 mb-2 adlign-items-stretch">
                <a href="use/introduction.html">
                    <div class="card rounded-lg" style="height:100%;">
                        <div class="d-flex">
                            <div>
                                <h3 class="card-title pl-3 mt-4">
                                Key Concepts
                                </h3>
                                <p class="mb-3 grey-text px-3">
                                    Learn about XCC features <i class="fas fa-angle-double-right"></i>
                                </p>
                            </div>
                        </div>
                    </div>
                </a>
            </div>
            <div class="col-lg-4 mb-2 align-items-stretch">
                <a href="dev/guide.html">
                <div class="card rounded-lg" style="height:100%;">
                    <div class="d-flex">
                        <div>
                            <h3 class="card-title pl-3 mt-4">
                            Getting Started
                            </h3>
                                <p class="mb-3 grey-text px-3">
                                    Learn how to quickly get started using the XCC <i class="fas fa-angle-double-right"></i>
                                </p>
                        </div>
                    </div>
                </div>
            </a>
            </div>
            <div class="col-lg-4 mb-2 align-items-stretch">
                <a href="api/library_root.html">
                <div class="card rounded-lg" style="height:100%;">
                    <div class="d-flex">
                        <div>
                            <h3 class="card-title pl-3 mt-4">
                            API
                            </h3>
                            <p class="mb-3 grey-text px-3">
                                Explore the XCC package <i class="fas fa-angle-double-right"></i>
                            </p>
                        </div>
                    </div>
                </div>
            </a>
            </div>
	    
        </div>
    </div>

Features
========

* *Simple.* Easy to setup, explore, and use.

..

* *Efficient.* Lazy fetching and caching by default.

..

* *Structured.* Parse Xanadu Cloud responses into JSON or Python objects.

Support
=======

- **Source Code:** https://github.com/XanaduAI/xanadu-cloud-client
- **Issue Tracker:** https://github.com/XanaduAI/xanadu-cloud-client/issues

If you are having issues, please let us know, either by email or by posting the
issue on our GitHub issue tracker.

License
=======

The XCC is **free** and **open source**, released under the Apache License, Version 2.0.

.. toctree::
   :maxdepth: 2
   :caption: Using the XCC
   :hidden:

   use/introduction

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