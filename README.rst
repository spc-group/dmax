===================================
dmax -- Data Management API Client
===================================

An (incomplete) alternative API client for data management systems at
the Advanced Photon Source that supports both synchronous and
asynchronous API calls.

.. image:: https://img.shields.io/pypi/v/dmax.svg
        :target: https://pypi.python.org/pypi/dmax
.. image:: https://github.com/spc-group/dmax/actions/workflows/ci.yml/badge.svg
        :target: https://github.com/spc-group/dmax/actions/workflows/ci.yml

Why dmax?
=========

The aps-dm-api package is available for accessing the various APIs in
python. Compared to aps-dm-api, *dmax* is:

- **Awaitable** - dmax has both a block and asynchronous client that share the same logic
- **Explicit** - parameters can be passed to a client rather than
  relying primarily on environmental variables.
- **On PyPI** - aps-dm-api can only be installed from conda-forge.

While we hope that *dmax* is useful, it is not intended as a complete
replacement for *aps-dm-api*. Features are added only as needed.
		 
Installation
============

The following will download the package and load it into the python environment.

.. code-block:: bash

    pip install dmax


Usage
=====

The main interface for *dmax* is the ``dmax.Client`` class, or its
asynchronous counterpart ``dmax.AsyncClient``.

*dmax* can be used either by as a **stand-alone** library, where the
data management API parameters are passed in explicitly, or embedded
in an **existing data-management environment**, where the API
connection parameters are defined in environmental variables.

Stand-alone
-----------

The client is given the login credentials, along with the station name
and any API URIs that it needs to connect.

.. code-block:: python

    import dmax
    
    client = dmax.Client(
        username="spam",
        password="secret",
        station_name="255IDZ",
        scheduling_uri: str = "https://example.com:11337",
        data_storage_uri: str = "https://example.com:22237",
        processing_uri: str = "https://example.com:55536",
    )
    
    proposals = client.proposals(cycle="2026-3")
    
    experiments = client.experiments()
    experiment = client.experiment(name="cabana-2026-3")

If the URI's are omitted, the client will attempt to guess sensible
defaults from the station name, for example `station_name="255IDZ"`
will produce URIs like `https://s255idzdm.xray.aps.anl.gov:55536`.

Embedded in a DM Environment
----------------------------

The APS data management system uses an extensive set of environmental
variables to handle the API parameters. If any parameters or not
provided to the client, environmental variables will be used if
available:

.. code-block:: python

    import dmax
    
    client = dmax.Client()
    
    esafs = client.esafs(year=2026)


Running the Tests
=================

.. code-block:: bash
		
    uv run --dev pytest
