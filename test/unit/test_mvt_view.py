from mock import patch, MagicMock

from rest_framework_mvt.views import BaseMVTView
from rest_framework.serializers import ValidationError
from django.test.client import RequestFactory


def test_BaseMVTView__get():
    base_mvt_view = BaseMVTView(geo_col="geom")
    model = MagicMock()
    vector_tiles = MagicMock()
    vector_tiles.intersect.return_value = b"mvt goes here"
    model.vector_tiles = vector_tiles
    base_mvt_view.model = model
    # request = MagicMock(query_params={"tile": "2/1/1"})
    request_factory = RequestFactory()
    request = request_factory.get("/hello", {"tile": "2/1/1"})

    response = base_mvt_view.get(request)

    assert response.status_code == 200
    assert response.data == b"mvt goes here"
    assert response.content_type == "application/vnd.mapbox-vector-tile"
    vector_tiles.intersect.assert_called_once()

    # Test path sources tile kwargs.
    request = request_factory.get("/hello")
    response = base_mvt_view.get(request, z=2, x=1, y=1)
    assert response.status_code == 200
    assert response.data == b"mvt goes here"
    assert response.content_type == "application/vnd.mapbox-vector-tile"

    # Test no tile arguments.
    response = base_mvt_view.get(request)
    assert response.status_code == 400
    assert response.data == b""
    assert response.content_type == "application/vnd.mapbox-vector-tile"


def test_BaseMVTView__intersects_validation_error_returns_400():
    base_mvt_view = BaseMVTView(geo_col="geom")
    model = MagicMock()
    vector_tiles = MagicMock()
    vector_tiles.intersect.side_effect = ValidationError("Invalid Parameters")
    model.vector_tiles = vector_tiles
    base_mvt_view.model = model
    request_factory = RequestFactory()
    request = request_factory.get("/hello", {"tile": "2/1/1"})

    response = base_mvt_view.get(request)

    assert response.status_code == 400
    assert response.data == b""
    assert response.content_type == "application/vnd.mapbox-vector-tile"


def test_BaseMVTView__does_not_pass_in_pagination_as_filters():
    base_mvt_view = BaseMVTView(geo_col="geom")
    model = MagicMock()
    vector_tiles = MagicMock()
    vector_tiles.intersect.return_value = b"mvt goes here"
    model.vector_tiles = vector_tiles
    base_mvt_view.model = model
    request_factory = RequestFactory()
    request = request_factory.get("/hello", {"tile": "2/1/1", "limit": 1, "offset": 1})

    response = base_mvt_view.get(request)

    assert response.status_code == 200
    assert response.data == b"mvt goes here"
    assert response.content_type == "application/vnd.mapbox-vector-tile"

    # TODO: fix this assertion.
    # request.GET.dict().pop.assert_called_with("offset", None)
    vector_tiles.intersect.assert_called_with(
        ["1", "1", "2"],
        limit=1,
        offset=1,
        filters={},
    )


def test_BaseMVTView__validate_paginate():
    limit, offset = BaseMVTView._validate_paginate("10", "7")

    assert limit == 10
    assert offset == 7


def test_BaseMVTView__validate_paginate_raises_ValidationError():
    try:
        limit, offset = BaseMVTView._validate_paginate("cat", "7")
        assert False
    except ValidationError:
        assert True
