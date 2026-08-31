from django.core.exceptions import FieldError
from django.contrib.gis.db import models
from rest_framework.serializers import ValidationError


class MVTManager(models.Manager):
    """
    Args:
        geo_col (str): Column name with the geometry. The default is "geom".
        source_name (str): Connection source to use.  If not provided the app's default
                           connection is used.
    """

    def __init__(self, *args, geo_col="geom", source_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.geo_col = geo_col
        self.source_name = source_name

    def intersect(self, bbox="", limit=-1, offset=0, filters={}):
        """
        Args:
            bbox (str): A string representing a bounding box, e.g., '-90,29,-89,35'.
            limit (int): Number of entries to include in the result.  The default
                         is -1 (includes all results).
            offset (int): Index to start collecting entries from.  Index size is the limit
                          size.  The default is 0.
            filters (dict): The keys represent column names and the values represent column
                            values to filter on.
        Returns:
            bytes:
            Bytes representing a Google Protobuf encoded Mapbox Vector Tile.  The
            vector tile will store each applicable row from the database as a
            feature.  Applicable rows fall within the passed in bbox.

        Raises:
            ValidationError: If filters include keys or values not accepted by
                             the manager's model.

        Note:
            The sql execution follows the guidelines from Django below.  As suggested, the executed
            query string does NOT contain quoted parameters.

            https://docs.djangoproject.com/en/2.2/topics/db/sql/#performing-raw-queries
        """
        limit = "ALL" if limit == -1 else limit
        query, parameters = self._build_query(filters=filters)
        with self._get_connection().cursor() as cursor:
            cursor.execute(query, [str(bbox), str(bbox)] + parameters + [limit, offset])
            mvt = cursor.fetchall()[-1][-1]  # should always return one tile on success
        return mvt

    def _get_non_geom_columns(self):
        """
        Retrieves all table columns that are NOT the defined geometry column
        """
        columns = []
        for field in self.model._meta.get_fields():
            if hasattr(field, "get_attname_column"):
                column_name = field.get_attname_column()[1]
                if column_name and column_name != self.geo_col:
                    columns.append(column_name)
        return columns

    def _build_query(self, filters={}):
        """
        Args:
            filters (dict): keys represent column names and values represent column
                            values to filter on.
        Returns:
            tuple:
            A tuple of length two.  The first element is a string representing a
            parameterized SQL query.  The second element is a list of parameters
            used as inputs to the query's WHERE clause.
        """
        table = self.model._meta.db_table.replace('"', "")
        select_statement = self._create_select_statement()
        (
            parameterized_where_clause,
            where_clause_parameters,
        ) = self._create_where_clause_with_params(table, filters)
        query = f"""
        SELECT NULL AS id, ST_AsMVT(q, 'default', 4096, 'mvt_geom')
            FROM (SELECT {select_statement}
                ST_AsMVTGeom(ST_Transform({table}.{self.geo_col}, 3857),
                ST_Transform(ST_SetSRID(ST_GeomFromText(%s), 4326), 3857), 4096, 0, false) AS mvt_geom
            FROM {table}
            WHERE {parameterized_where_clause}
            LIMIT %s
            OFFSET %s) AS q;
        """
        return (query.strip(), where_clause_parameters)

    def _create_where_clause_with_params(self, table, filters):
        """
        Args:
            table (str): A string representing the name of the table to query on.
            filters (dict): keys represent column names and values represent column
                            values to filter on.
        Returns:
            tuple:
            A tuple of length two.  The first element is a string representing a
            parameterized SQL query WHERE clause.  The second element is a list
            of parameters used as inputs to the WHERE clause.
        """
        try:
            sql, params = self.filter(**filters).query.sql_with_params()
        except FieldError as error:
            raise ValidationError(str(error)) from error
        extra_wheres = " AND " + sql.split("WHERE")[1].strip() if params else ""
        where_clause = (
            f"ST_Intersects({table}.{self.geo_col}, "
            f"ST_SetSRID(ST_GeomFromText(%s), 4326)){extra_wheres}"
        )
        return where_clause, list(params)

    def _create_select_statement(self):
        """
        Create a SELECT statement that only includes columns defined on the
        model.  Each column must be named in the SELECT statement to specify
        only the required columns.  Including the geom column raises an error
        in the PostGIS ST_AsMVT function.

        Returns:
            str:
            A string representing a parameterized SQL query SELECT statement.
        """
        columns = self._get_non_geom_columns()
        sql, _ = self.only(*columns).query.sql_with_params()
        select_sql = sql.split("FROM")[0].lstrip("SELECT ").strip() + ","
        return select_sql

    def _get_connection(self):
        """

        Returns:
            (django.db.connection):
            The 'default' Django database connection if source_name is not defined on the instance.
        """
        # pylint: disable=import-outside-toplevel
        from django.db import connection, connections

        return connection if self.source_name is None else connections[self.source_name]
