import json
import logging

from django.contrib.gis.gdal.error import GDALException
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.error import GEOSException
from django.db import connection
from django.db.models import ObjectDoesNotExist, QuerySet

from common.constants import GeoFeatureClass, Length
from geo.api.serializers import GeoFeatureDetailSerializer, GeoFeatureSerializer
from geo.models import SRID_WGS84, UPLOADED_FEATURE_ID_SEQ, GeoFeature, GeoFeatureUser

from .error_codes import ErrorCode

logger = logging.getLogger(__name__)

# Upper bound for nearest lookups, meters. Bounds the ST_DWithin scan.
MAX_RADIUS_M = 50_000

# The geom column is a 4326 geometry, so meter-based spatial predicates
# must run on geography. Served by the (geom::geography) GiST index.
DWITHIN_SQL = "ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)"
DISTANCE_SQL = "ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)"

# Valid lat/lng ranges in WGS84
LAT_MIN, LAT_MAX = -90, 90
LNG_MIN, LNG_MAX = -180, 180

POLYGON_TYPES = ("Polygon", "MultiPolygon")

# Upload bounds: geometry size cap keeps requests and stored rows small
MAX_UPLOAD_POINTS = 10_000


def svc_geo_helper_get_fclasses(raw_fclass, csv: bool = False):
    """
    fclass can be a csv (GET query param) or a list (POST within body).
    Empty means: all classes.
    """

    logger.debug(f">> ARGS: {locals()}")

    if not raw_fclass:
        return None, []

    fclasses = raw_fclass.split(",") if csv else raw_fclass

    for fclass in fclasses:
        try:
            GeoFeatureClass.from_string(fclass.strip() if csv else fclass)
        except ValueError:
            return ErrorCode(ErrorCode.INVALID_FCLASS, fclass=fclass), None

    return None, [fclass.strip() if csv else fclass for fclass in fclasses]


def svc_geo_helper_parse_polygon(polygon):
    logger.debug(f">> ARGS: {locals()}")

    if not isinstance(polygon, dict):
        return ErrorCode(ErrorCode.INVALID_POLYGON, error="polygon must be a GeoJSON geometry"), None

    try:
        geom = GEOSGeometry(json.dumps(polygon))
    except (ValueError, TypeError, GEOSException) as e:
        return ErrorCode(ErrorCode.INVALID_POLYGON, error=repr(e)), None

    if geom.geom_type not in POLYGON_TYPES or not geom.valid:
        return ErrorCode(ErrorCode.INVALID_POLYGON, error=f"not a valid {POLYGON_TYPES}"), None

    geom.srid = SRID_WGS84

    return None, geom


def svc_geo_helper_parse_upload_geometry(geometry):
    """Any valid, non-empty GeoJSON geometry (one feature per request)"""

    logger.debug(f">> ARGS: {locals()}")

    if not isinstance(geometry, dict):
        return ErrorCode(ErrorCode.INVALID_GEOMETRY, error="geometry must be a GeoJSON geometry"), None

    try:
        geom = GEOSGeometry(json.dumps(geometry))
    except (ValueError, TypeError, GEOSException, GDALException) as e:
        return ErrorCode(ErrorCode.INVALID_GEOMETRY, error=repr(e)), None

    if geom.empty or not geom.valid:
        return ErrorCode(ErrorCode.INVALID_GEOMETRY, error="empty or topologically invalid geometry"), None

    if geom.num_points > MAX_UPLOAD_POINTS:
        return ErrorCode(ErrorCode.INVALID_GEOMETRY, error=f"more than {MAX_UPLOAD_POINTS} points"), None

    geom.srid = SRID_WGS84

    return None, geom


def svc_geo_helper_get_next_uploaded_feature_id() -> int:
    """Ids for uploads come from the offset sequence, not the packed
    OSM ids the import assigns: ids must stay unique across the
    geo_feature view, since callers resolve them without knowing the
    storage table."""

    logger.debug(f">> ARGS: {locals()}")

    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval(%s)", [UPLOADED_FEATURE_ID_SEQ])
        return cursor.fetchone()[0]


def svc_geo_helper_create_uploaded_feature(request_data: dict, uploaded_by):
    """Validate one uploaded feature and store it in geo_feature_user.
    Body: {"name", "fclass", "geometry": {GeoJSON}, "tags": {optional}}

    Returns the feature as GeoFeature (the view): the source and
    osm_id fields and the GeoJSON methods live there, not on the
    write model.
    """

    logger.debug(f">> ARGS: {locals()}")

    name = request_data.get("name")
    if name is None:
        return ErrorCode(ErrorCode.MISSING_NAME), None

    name = str(name).strip()
    if not name or len(name) > Length.GEO_FEATURE_NAME:
        return ErrorCode(ErrorCode.INVALID_NAME), None

    fclass = request_data.get("fclass")
    try:
        GeoFeatureClass.from_string(fclass)
    except ValueError:
        return ErrorCode(ErrorCode.INVALID_FCLASS, fclass=fclass), None

    if request_data.get("geometry") is None:
        return ErrorCode(ErrorCode.MISSING_GEOMETRY), None

    error, geom = svc_geo_helper_parse_upload_geometry(request_data["geometry"])
    if error:
        return error, None

    tags = request_data.get("tags") or {}
    if not isinstance(tags, dict):
        return ErrorCode(ErrorCode.INVALID_TAGS), None

    feature_id = svc_geo_helper_get_next_uploaded_feature_id()

    GeoFeatureUser.create_uploaded(
        feature_id=feature_id,
        uploaded_by=uploaded_by,
        name=name,
        feature_class=fclass,
        geom=geom,
        tags=tags,
    )

    return None, GeoFeature.objects.get(id=feature_id)


def svc_geo_helper_get_features(fclasses: list[str]) -> QuerySet:
    logger.debug(f">> ARGS: {locals()}")

    features = GeoFeature.objects.order_by("name")

    if fclasses:
        features = features.filter(feature_class__in=fclasses)

    return features


def svc_geo_helper_get_feature_by_id(feature_id: int):
    logger.debug(f">> ARGS: {locals()}")

    try:
        return None, GeoFeature.objects.get(id=feature_id)
    except (ObjectDoesNotExist, ValueError):
        return ErrorCode(ErrorCode.INVALID_FEATURE_ID, feature_id=feature_id), None


def svc_geo_helper_get_features_within(polygon: GEOSGeometry, fclasses: list[str]) -> QuerySet:
    """ST_Intersects(geom, polygon) — candidate features inside the play area"""

    logger.debug(f">> ARGS: {locals()}")

    features = GeoFeature.objects.filter(geom__intersects=polygon)

    if fclasses:
        features = features.filter(feature_class__in=fclasses)

    return features.order_by("name")


def svc_geo_helper_get_serialized_features(features, many: bool, detail: bool = False):
    logger.debug(f">> ARGS: {locals()}")

    serializer = GeoFeatureDetailSerializer if detail else GeoFeatureSerializer

    return serializer(features, many=many).data
