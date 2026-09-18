from datetime import date
from . import create_app
from .extensions import db
from .models import User,Project,Site,Metric
from .geo import geojson_to_db

app=create_app()
with app.app_context():
    db.drop_all();db.create_all()
    u=User(name="Demo Admin",email="demo@darukaa.earth");u.set_password("DarukaaDemo123!");db.session.add(u);db.session.flush()
    p=Project(name="Maharashtra Restoration",description="Demo carbon and biodiversity monitoring project",owner_id=u.id);db.session.add(p);db.session.flush()
    polygons=[
      ("Wardha Agroforestry",77.75,20.75,[(77.70,20.70),(77.80,20.70),(77.80,20.80),(77.70,20.80),(77.70,20.70)]),
      ("Satara Habitat Corridor",74.00,17.70,[(73.95,17.65),(74.05,17.65),(74.05,17.75),(73.95,17.75),(73.95,17.65)])
    ]
    for idx,(name,lon,lat,coords) in enumerate(polygons):
        geom={"type":"Polygon","coordinates":[coords]}
        s=Site(project_id=p.id,name=name,geometry=geojson_to_db(geom),area_hectares=100,latitude=lat,longitude=lon)
        db.session.add(s);db.session.flush()
        for j in range(6):
            db.session.add(Metric(site_id=s.id,observed_on=date(2026,1+j,15),
                carbon_tco2e=120+j*8+idx*12,biodiversity_index=0.42+j*.035-idx*.01,
                tree_cover_pct=31+j*1.7+idx*4,soil_organic_carbon_pct=.55+j*.035,rainfall_mm=55+j*18))
    db.session.commit()
    print("Seeded demo data.")
