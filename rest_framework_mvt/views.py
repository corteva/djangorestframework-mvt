from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_gis.filters import TMSTileFilter
from rest_framework_mvt.renderers import BinaryRenderer
from rest_framework_mvt.schemas import MVT_SCHEMA


class BaseMVTView(APIView):
    """
    Base view for serving a model as a Mapbox Vector Tile given X/Y/Z tile constraints.
    """

    model = None
    geom_col = None
    renderer_classes = (BinaryRenderer,)
    schema = MVT_SCHEMA

    # pylint: disable=unused-argument
    def get(self, request, *args, **kwargs):
        """
        Args:
            request (:py:class:`rest_framework.request.Request`): Standard DRF request object
        Returns:
            :py:class:`rest_framework.response.Response`:  Standard DRF response object
        """
        params = request.GET.dict()
        if params.pop("tile", None) is not None:
            try:
                limit, offset = self._validate_paginate(
                    params.pop("limit", None), params.pop("offset", None)
                )
            except ValidationError:
                limit, offset = None, None
            bbox = TMSTileFilter().get_filter_bbox(request)
            try:
                mvt = self.model.vector_tiles.intersect(
                    bbox=bbox, limit=limit, offset=offset, filters=params
                )
                status = 200 if mvt else 204
            except ValidationError:
                mvt = b""
                status = 400
        else:
            mvt = b""
            status = 400

        return Response(
            bytes(mvt), content_type="application/vnd.mapbox-vector-tile", status=status
        )

    @staticmethod
    def _validate_paginate(limit, offset):
        """
        Attempts to convert given limit and offset as strings to integers.
        Args:
            limit (str): A string representing the size of the pagination request
            offset (str): A string representing the starting index of the pagination request
        Returns:
            tuple:
            A tuple of length two.  The first element is an integer representing
            the limit.  The second element is an integer representing the offset.
        Raises:
            `rest_framework.serializers.ValidationError`: if limit or offset can't be cast
                                                        to an integer
        """
        if limit is not None and offset is not None:
            try:
                limit, offset = int(limit), int(offset)
            except ValueError as value_error:
                raise ValidationError(
                    "Query param validation error: " + str(value_error)
                ) from value_error

        return limit, offset


def mvt_view_factory(model_class, geom_col="geom"):
    """
    Creates an MVTView that serves Mapbox Vector Tiles for the
    given model and geom column.

    Args:
        model_class (:py:class:`django.contrib.gis.db.models.Model`): A GeoDjango model
        geom_col (str): A string representing the column name containing
                        PostGIS geometry types.
    Returns:
        :py:class:`rest_framework_mvt.views.MVTView`:
        A subclass of :py:class:`rest_framework_mvt.views.MVTView` with its geom_col
        and model set to the function's passed in values.
    """
    return type(
        f"{model_class.__name__}MVTView",
        (BaseMVTView,),
        {"model": model_class, "geom_col": geom_col},
    ).as_view()
