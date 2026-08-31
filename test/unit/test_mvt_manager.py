from django.core.exceptions import FieldError
from rest_framework_mvt.managers import MVTManager
from rest_framework.serializers import ValidationError
from mock import patch, MagicMock
import pytest


@pytest.fixture
def mvt_manager():
    mvt_manager = MVTManager(geo_col="jazzy_geo")
    meta = MagicMock(db_table="test_table")
    fields = [
        MagicMock(
            get_attname_column=MagicMock(return_value=("other_column", "other_column"))
        ),
        MagicMock(
            get_attname_column=MagicMock(return_value=("jazzy_geo", "jazzy_geo"))
        ),
        MagicMock(get_attname_column=MagicMock(return_value=("city", "city"))),
    ]
    meta.get_fields.return_value = fields
    mvt_manager.model = MagicMock(_meta=meta)

    return mvt_manager


@pytest.fixture
def mvt_manager_no_col():
    mvt_manager_no_col = MVTManager()
    meta = MagicMock(db_table="test_table")
    fields = [
        MagicMock(
            get_attname_column=MagicMock(return_value=("other_column", "other_column"))
        ),
        MagicMock(
            get_attname_column=MagicMock(return_value=("jazzy_geo", "jazzy_geo"))
        ),
        MagicMock(get_attname_column=MagicMock(return_value=("city", "city"))),
        MagicMock(
            get_attname_column=MagicMock(return_value=("generic_relation", None))
        ),
    ]
    meta.get_fields.return_value = fields
    mvt_manager_no_col.model = MagicMock(_meta=meta)

    return mvt_manager_no_col


@patch("rest_framework_mvt.managers.MVTManager._get_connection")
def test_mvt_manager_intersect__calls__build_query(get_conn, mvt_manager):
    mvt_manager._build_query = MagicMock()
    mvt_manager._build_query.return_value = ("foo", ["bar"])

    mvt_manager.intersect(bbox="", limit=10, offset=7)

    mvt_manager._build_query.assert_called_once_with(filters={})


@patch("rest_framework_mvt.managers.MVTManager.only")
@patch("rest_framework_mvt.managers.MVTManager._get_connection")
def test_mvt_manager_build_query__all(get_conn, only, mvt_manager):
    query = MagicMock()
    query.sql_with_params.return_value = ("SELECT other_column, city FROM table", [])
    only.return_value = MagicMock(query=query)
    expected_query = """
        SELECT NULL AS id, ST_AsMVT(q, 'default', 4096, 'mvt_geom')
            FROM (SELECT other_column, city,
                ST_AsMVTGeom(ST_Transform(test_table.jazzy_geo, 3857),
                ST_Transform(ST_SetSRID(ST_GeomFromText(%s), 4326), 3857), 4096, 0, false) AS mvt_geom
            FROM test_table
            WHERE ST_Intersects(test_table.jazzy_geo, ST_SetSRID(ST_GeomFromText(%s), 4326))
            LIMIT %s
            OFFSET %s) AS q;
    """.strip()
    expected_parameters = []

    query, parameters = mvt_manager._build_query()

    assert expected_query == query
    assert expected_parameters == parameters


@patch("rest_framework_mvt.managers.MVTManager.only")
@patch("rest_framework_mvt.managers.MVTManager._get_connection")
def test_mvt_manager_build_query__no_geo_col(get_conn, only, mvt_manager_no_col):
    query = MagicMock()
    query.sql_with_params.return_value = ("SELECT other_column, city FROM table", [])
    only.return_value = MagicMock(query=query)
    expected_query = """
        SELECT NULL AS id, ST_AsMVT(q, 'default', 4096, 'mvt_geom')
            FROM (SELECT other_column, city,
                ST_AsMVTGeom(ST_Transform(test_table.geom, 3857),
                ST_Transform(ST_SetSRID(ST_GeomFromText(%s), 4326), 3857), 4096, 0, false) AS mvt_geom
            FROM test_table
            WHERE ST_Intersects(test_table.geom, ST_SetSRID(ST_GeomFromText(%s), 4326))
            LIMIT %s
            OFFSET %s) AS q;
    """.strip()
    expected_parameters = []

    query, parameters = mvt_manager_no_col._build_query()

    assert expected_query == query
    assert expected_parameters == parameters
    only.assert_called_once_with("other_column", "jazzy_geo", "city")


@patch("rest_framework_mvt.managers.MVTManager.filter")
@patch("rest_framework_mvt.managers.MVTManager.only")
@patch("rest_framework_mvt.managers.MVTManager._get_connection")
def test_mvt_manager_build_query__filter(get_conn, only, orm_filter, mvt_manager):
    query = MagicMock()
    query.sql_with_params.return_value = (
        "SELECT other_column, city FROM table WHERE (city = %s)",
        ["johnston"],
    )
    only.return_value = MagicMock(query=query)
    orm_filter.return_value = MagicMock(query=query)
    expected_query = """
        SELECT NULL AS id, ST_AsMVT(q, 'default', 4096, 'mvt_geom')
            FROM (SELECT other_column, city,
                ST_AsMVTGeom(ST_Transform(test_table.jazzy_geo, 3857),
                ST_Transform(ST_SetSRID(ST_GeomFromText(%s), 4326), 3857), 4096, 0, false) AS mvt_geom
            FROM test_table
            WHERE ST_Intersects(test_table.jazzy_geo, ST_SetSRID(ST_GeomFromText(%s), 4326)) AND (city = %s)
            LIMIT %s
            OFFSET %s) AS q;
    """.strip()
    expected_parameters = ["johnston"]

    query, parameters = mvt_manager._build_query(filters={"city": "johnston"})

    assert expected_query == query
    assert expected_parameters == parameters


@patch("rest_framework_mvt.managers.MVTManager.filter")
@patch("rest_framework_mvt.managers.MVTManager.only")
@patch("rest_framework_mvt.managers.MVTManager._get_connection")
def test_mvt_manager_build_query__multiple_filters(
    get_conn, only, orm_filter, mvt_manager
):
    query = MagicMock()
    query.sql_with_params.return_value = (
        "SELECT other_column, city FROM table WHERE (city = %s AND other_column = %s)",
        ["johnston", "IA"],
    )
    only.return_value = MagicMock(query=query)
    orm_filter.return_value = MagicMock(query=query)
    expected_query = """
        SELECT NULL AS id, ST_AsMVT(q, 'default', 4096, 'mvt_geom')
            FROM (SELECT other_column, city,
                ST_AsMVTGeom(ST_Transform(test_table.jazzy_geo, 3857),
                ST_Transform(ST_SetSRID(ST_GeomFromText(%s), 4326), 3857), 4096, 0, false) AS mvt_geom
            FROM test_table
            WHERE ST_Intersects(test_table.jazzy_geo, ST_SetSRID(ST_GeomFromText(%s), 4326)) AND (city = %s AND other_column = %s)
            LIMIT %s
            OFFSET %s) AS q;
    """.strip()
    expected_parameters = ["johnston", "IA"]

    query, parameters = mvt_manager._build_query(
        filters={"city": "johnston", "other_column": "IA"}
    )

    assert expected_query == query
    assert expected_parameters == parameters


@patch("rest_framework_mvt.managers.MVTManager.filter")
@patch("rest_framework_mvt.managers.MVTManager.only")
@patch("rest_framework_mvt.managers.MVTManager._get_connection")
def test_mvt_manager_build_query__validation_error(
    get_conn, only, orm_filter, mvt_manager
):
    query = MagicMock()
    query.sql_with_params.return_value = (
        "SELECT other_column, city FROM table WHERE (city = %s AND other_column = %s)",
        ["johnston", "IA"],
    )
    only.return_value = MagicMock(query=query)
    orm_filter.side_effect = FieldError

    with pytest.raises(ValidationError) as e:
        query = mvt_manager._build_query(filters={"not_a_filter": "oops"})


@patch("rest_framework_mvt.managers.MVTManager.filter")
@patch("rest_framework_mvt.managers.MVTManager._get_connection")
def test_mvt_manager_create_where_clause_with_params(get_conn, orm_filter, mvt_manager):
    query_filter = MagicMock()
    query_filter.sql_with_params.return_value = (
        (
            'SELECT "my_schema"."my_table"."id", "my_schema"."my_table"."foreign_key_id", '
            '"my_schema"."my_table"."col_1", "my_schema"."my_table"."geom"::bytea FROM '
            '"my_schema"."my_table" WHERE ("my_schema"."my_table"."col_1" = %s AND '
            '"my_schema"."my_table"."foreign_key_id" = %s)'
        ),
        ("filter_1", 1),
    )
    orm_filter.return_value = MagicMock(query=query_filter)

    (
        parameterized_where_clause,
        where_clause_parameters,
    ) = mvt_manager._create_where_clause_with_params(
        "my_schema.my_table", {"col_1": "filter_1", "foreign_key": 1}
    )

    orm_filter.assert_called_once_with(col_1="filter_1", foreign_key=1)
    query_filter.sql_with_params.assert_called_once()
    assert parameterized_where_clause == (
        "ST_Intersects(my_schema.my_table.jazzy_geo, ST_SetSRID(ST_GeomFromText(%s), 4326)) "
        'AND ("my_schema"."my_table"."col_1" = %s AND "my_schema"."my_table"."foreign_key_id" = %s)'
    )
    assert where_clause_parameters == ["filter_1", 1]
