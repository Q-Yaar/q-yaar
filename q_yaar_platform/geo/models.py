import json

from django.contrib.gis.db import models as gis_models
from django.db import models

from common.abstract_models import AbstractTimeStamped
from common.constants import GeoFeatureClass, GeoFeatureSource, GeoImportStatus, Length

SRID_WGS84 = 4326

# Ids for uploaded features come from this sequence, whose START sits far
# below the packed OSM ids the import assigns (type bits from 2^61 up,
# docker/geo/flex.lua), so upload ids never collide with them
# (geo/migrations/0001, created together with the table).
UPLOADED_FEATURE_ID_SEQ = "geo_feature_user_id_seq"


class GeoFeature(AbstractTimeStamped, models.Model):
    """
    Read model over the geo_feature view: a UNION ALL of
    geo_feature_imported (docker/geo) and geo_feature_user. The view
    is the one read path — queries, serializers, inline blobs treat
    every feature identically, no matter which table stores it.
    A view, not a table, so Django cannot manage it.

    Not writable. The two write sides are the import job (GeoFeatureImported)
    and the upload endpoint (GeoFeatureUser.create_uploaded).

    Ids are stable across imports: OSM row ids are packed from the OSM
    identity (osm_type << 61 | osm_id, docker/geo/flex.lua), the
    Datameet row id is a name hash (import.sh), so a feature that
    survives a re-import keeps its id. Clients fetch a feature's
    geometry from the read endpoints and attach it to
    questions/answers/facts themselves, so a re-import never touches
    stored questions, answers or facts.

    An area is any feature with a polygon geom (city, ward, Cubbon Park),
    so new play areas need no schema or import changes.
    """

    # Packed from the OSM identity, hashed from the name for Datameet
    # rows, or drawn from UPLOADED_FEATURE_ID_SEQ for uploads (three
    # disjoint id spaces, see above).
    id = models.BigIntegerField(primary_key=True)
    osm_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=Length.GEO_FEATURE_NAME, blank=True, null=False, default="")
    feature_class = models.CharField(
        max_length=Length.GEO_FEATURE_CLASS, choices=GeoFeatureClass.get_choices(), db_column="fclass"
    )
    source = models.CharField(
        max_length=Length.GEO_FEATURE_SOURCE,
        choices=GeoFeatureSource.get_choices(),
        default=GeoFeatureSource.OSM.value,
    )
    tags = models.JSONField(default=dict, blank=True)
    geom = gis_models.GeometryField(srid=SRID_WGS84)

    # NULL for every imported feature; the view fills it from
    # geo_feature_user for uploads. No reverse accessor: nothing
    # navigates from a user to the view; use GeoFeatureUser's
    # uploaded_geo_features instead.
    uploaded_by = models.ForeignKey(
        "account.PlatformUser",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        db_column="uploaded_by",
        db_constraint=False,
    )

    class Meta:
        managed = False
        db_table = "geo_feature"

    def __str__(self):
        return f"{self.feature_class}:{self.name}({self.osm_id})"

    def get_location_dict(self):
        """Compact {lat, lng}: the point itself for POIs, centroid for areas"""

        geom = self.geom
        point = geom if geom.geom_type == "Point" else geom.centroid

        return {"lat": point.y, "lng": point.x}

    def get_geojson(self):
        """GeoJSON geometry dict, as stored, ready for the client to draw"""

        return json.loads(self.geom.geojson)


class GeoFeatureImported(AbstractTimeStamped, models.Model):
    """
    Managed write side of geo_feature_imported: the rows the import
    job owns (source='osm' and source='datameet'). The import replaces
    them wholesale — TRUNCATE + INSERT in one transaction
    (docker/geo/import.sh) — so the table identity, and with it the
    view and indexes, stay fixed. The app itself never writes here;
    this model exists so Django owns the DDL and UTs can seed
    imported-style features, which the view then serves like any other.
    """

    id = models.BigIntegerField(primary_key=True)
    osm_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=Length.GEO_FEATURE_NAME, blank=True, null=False, default="")
    feature_class = models.CharField(
        max_length=Length.GEO_FEATURE_CLASS, choices=GeoFeatureClass.get_choices(), db_column="fclass"
    )
    source = models.CharField(
        max_length=Length.GEO_FEATURE_SOURCE,
        choices=GeoFeatureSource.get_choices(),
        default=GeoFeatureSource.OSM.value,
    )
    tags = models.JSONField(default=dict, blank=True)
    # Indexes are hand-created (geo/migrations/0001): geometry GiST plus
    # geom::geography GiST for meter-based ST_DWithin lookups, both with
    # stable names the import job relies on
    geom = gis_models.GeometryField(srid=SRID_WGS84, spatial_index=False)

    class Meta:
        db_table = "geo_feature_imported"

    def __str__(self):
        return f"{self.feature_class}:{self.name}({self.osm_id})"


class GeoFeatureUser(AbstractTimeStamped, models.Model):
    """
    Managed write side of geo_feature_user: API-uploaded features.
    The only geo table the app writes; the import job never touches
    it, so uploads survive imports by construction.

    source is implicit ('user') — the geo_feature view supplies it.

    Uploaded features are shared reference data: they outlive their
    uploader (other users' questions anchor on them), so a deleted
    account orphans the feature instead of cascading it away
    (uploaded_by is a real FK with ON DELETE SET NULL).
    """

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=Length.GEO_FEATURE_NAME, blank=True, null=False, default="")
    feature_class = models.CharField(
        max_length=Length.GEO_FEATURE_CLASS, choices=GeoFeatureClass.get_choices(), db_column="fclass"
    )
    tags = models.JSONField(default=dict, blank=True)
    geom = gis_models.GeometryField(srid=SRID_WGS84, spatial_index=False)
    # db_constraint=False: Django can't express ON DELETE SET NULL as
    # DB-level DDL (it enforces on_delete in the ORM only). The real
    # constraint, with ON DELETE SET NULL and a canonical name, is
    # created by geo/migrations/0001 — never altered by Django after.
    uploaded_by = models.ForeignKey(
        "account.PlatformUser",
        on_delete=models.SET_NULL,
        related_name="uploaded_geo_features",
        null=True,
        db_column="uploaded_by",
        db_constraint=False,
    )

    class Meta:
        db_table = "geo_feature_user"

    def __str__(self):
        return f"{self.feature_class}:{self.name}"

    @classmethod
    def create_uploaded(cls, *, feature_id: int, uploaded_by, name: str, feature_class: str, geom, tags: dict):
        """One API-uploaded feature. feature_id comes from UPLOADED_FEATURE_ID_SEQ."""

        feature = cls(
            id=feature_id,
            name=name,
            feature_class=feature_class,
            tags=tags,
            geom=geom,
            uploaded_by=uploaded_by,
        )
        feature.save()

        return feature


class GeoImport(models.Model):
    """
    Run metadata for one osm2pgsql run: what was imported, when, and
    how far it got. Rows are written only by the import job; the app
    reads them for diagnostics. Django owns the DDL (geo/migrations).
    """

    id = models.BigAutoField(primary_key=True)
    source = models.CharField(max_length=Length.GEO_IMPORT_SOURCE)
    started = models.DateTimeField()
    finished = models.DateTimeField(blank=True, null=True)
    feature_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=Length.GEO_IMPORT_STATUS, choices=GeoImportStatus.get_choices())

    class Meta:
        db_table = "geo_import"

    def __str__(self):
        return f"{self.source}:{self.status}"
