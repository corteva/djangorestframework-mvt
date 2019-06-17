from mock import patch, MagicMock

from rest_framework_mvt.views import BaseMVTView
from rest_framework.serializers import ValidationError


@patch("rest_framework_mvt.views.TMSTileFilter")
def test_BaseMVTView__get(tile_filter):
    base_mvt_view = BaseMVTView(geo_col="geom")
    model = MagicMock()
    vector_tiles = MagicMock()
    vector_tiles.intersect.return_value = b"mvt goes here"
    model.vector_tiles = vector_tiles
    base_mvt_view.model = model
    request = MagicMock(query_params={"tile": "2/1/1"})

    response = base_mvt_view.get(request)

    assert response.status_code == 200
    assert response.data == b"mvt goes here"
    assert response.content_type == "application/vnd.mapbox-vector-tile"
    vector_tiles.intersect.assert_called_once()


@patch("rest_framework_mvt.views.TMSTileFilter")
def test_BaseMVTView__intersects_validation_error_returns_400(tile_filter):
    base_mvt_view = BaseMVTView(geo_col="geom")
    model = MagicMock()
    vector_tiles = MagicMock()
    vector_tiles.intersect.side_effect = ValidationError("Invalid Parameters")
    model.vector_tiles = vector_tiles
    base_mvt_view.model = model
    request = MagicMock(query_params={"tile": "2/1/1"})

    response = base_mvt_view.get(request)

    assert response.status_code == 400
    assert response.data == b""
    assert response.content_type == "application/vnd.mapbox-vector-tile"


@patch("rest_framework_mvt.views.TMSTileFilter")
def test_BaseMVTView__does_not_pass_in_pagination_as_filters(tile_filter):
    base_mvt_view = BaseMVTView(geo_col="geom")
    model = MagicMock()
    vector_tiles = MagicMock()
    vector_tiles.intersect.return_value = b"mvt goes here"
    model.vector_tiles = vector_tiles
    base_mvt_view.model = model
    request = MagicMock(query_params={"tile": "2/1/1", "limit": 1, "offset": 1})

    response = base_mvt_view.get(request)

    assert response.status_code == 200
    assert response.data == b"mvt goes here"
    assert response.content_type == "application/vnd.mapbox-vector-tile"
    request.GET.dict().pop.assert_called_with("offset", None)
    vector_tiles.intersect.assert_called_with(
        bbox=tile_filter().get_filter_bbox(),
        limit=1,
        offset=1,
        filters=request.GET.dict(),
    )


@patch("rest_framework_mvt.views.TMSTileFilter")
def test_BaseMVTView__validate_paginate(tile_filter):
    limit, offset = BaseMVTView._validate_paginate("10", "7")

    assert limit == 10
    assert offset == 7


@patch("rest_framework_mvt.views.TMSTileFilter")
def test_BaseMVTView__validate_paginate_raises_ValidationError(tile_filter):
    try:
        limit, offset = BaseMVTView._validate_paginate("cat", "7")
        assert False
    except ValidationError:
        assert True
