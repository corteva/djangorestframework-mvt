import coreapi
from rest_framework.schemas import ManualSchema
from rest_framework.compat import coreschema

MVT_SCHEMA = ManualSchema(
    fields=[
        coreapi.Field(
            "tile",
            required=True,
            location="query",
            schema=coreschema.String(
                description="TMS coordinates of the requested tile. The format should be tile=z/x/y"
            ),
        ),
        coreapi.Field(
            "limit",
            required=False,
            location="query",
            schema=coreschema.String(
                description="Number of results to return per page."
            ),
        ),
        coreapi.Field(
            "offset",
            required=False,
            location="query",
            schema=coreschema.String(
                description="The initial index from which to return the results."
            ),
        ),
    ]
)
