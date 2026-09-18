from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import transform
from pyproj import Transformer

def geojson_to_db(obj):
    geom=shape(obj)
    if isinstance(geom, Polygon): geom=MultiPolygon([geom])
    return from_shape(geom, srid=4326)

def db_to_geojson(value):
    return mapping(to_shape(value)) if value else None

def polygon_area_hectares(obj):
    geom=shape(obj)
    transformer=Transformer.from_crs(4326,6933,always_xy=True).transform
    return transform(transformer,geom).area/10000
