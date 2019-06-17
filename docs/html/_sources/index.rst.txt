Welcome to djangorestframework-mvt's documentation!
===================================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:

System Requirements
===================
* `GDAL >= 2.1 <https://gdal.org>`_
* `Postgres >= 10 <https://www.postgresql.org/download/>`_
* `PostGIS >= 2.4.0 <http://postgis.net/install/>`_
* Python >= 3.0

Installation
============

.. code-block:: bash

    pip install djangorestframework-mvt

Getting Started
===============
In a project's `models.py` file add a `MVTManager` to a model
to be served as Mapbox Vector Tiles.  For example:

.. code-block:: python

    from django.contrib.gis.db import models
    from rest_framework_mvt.managers import MVTManager

    class Example(models.Model):
        geom = models.PointField()
        my_column = models.CharField()
        objects = models.Manager()
        vector_tiles = MVTManager()

The `geo_col` keyword argument specifies the name of the PostGIS
geometry typed column.

In the project's `urls.py`, create a view linked to a model using
a `MVTManager` with the `mvt_view_factory` function. For example:

.. code-block:: python

    from rest_framework_mvt.views import mvt_view_factory

    urlpatterns = [
        path("api/v1/data/example.mvt/", mvt_view_factory(Example)),
    ]

The following requests should now be enabled:

.. sourcecode:: http

  GET api/v1/data/example.mvt?tile=1/0/0 HTTP/1.1

.. sourcecode:: http

  GET api/v1/data/example.mvt?tile=1/0/0&my_column=foo HTTP/1.1

.. sourcecode:: http

  GET api/v1/data/example.mvt?tile=1/0/0&my_column=foo&limit=10 HTTP/1.1

.. sourcecode:: http

  GET api/v1/data/example.mvt?tile=1/0/0&my_column=foo&limit=10&offset=10 HTTP/1.1

References
==========
- `Mapbox Vector Tile Introduction <https://docs.mapbox.com/vector-tiles/reference/>`_
- `Mapbox Vector Tile v2.1 Specification <https://github.com/mapbox/vector-tile-spec/tree/master/2.1/>`_
- `Google Protocol Buffers <https://developers.google.com/protocol-buffers/>`_
- `PostGIS ST_AsMVT <https://postgis.net/docs/ST_AsMVT.html>`_
- If deploying to AWS RDS Postgres, version 10.5+ is required.  See `here <https://forums.aws.amazon.com/thread.jspa?threadID=277371>`_ for more info.

Source Documentation
====================
.. automodule:: rest_framework_mvt.managers
    :members:
.. automodule:: rest_framework_mvt.views
    :members:
.. toctree::
   :maxdepth: 2
   :caption: Contents
