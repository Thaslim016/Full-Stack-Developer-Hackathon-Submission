from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from geoalchemy2 import Geometry
from sqlalchemy import func
from .extensions import db

class User(db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    email=db.Column(db.String(255),unique=True,nullable=False,index=True)
    password_hash=db.Column(db.String(255),nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    projects=db.relationship("Project",backref="owner",lazy=True)
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)

class Project(db.Model):
    __tablename__="projects"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(160),nullable=False)
    description=db.Column(db.Text,default="")
    status=db.Column(db.String(30),default="active")
    owner_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    sites=db.relationship("Site",backref="project",lazy=True,cascade="all, delete-orphan")
    def to_dict(self):
        return {"id":self.id,"name":self.name,"description":self.description,"status":self.status,
                "site_count":len(self.sites),"created_at":self.created_at.isoformat()}

class Site(db.Model):
    __tablename__="sites"
    id=db.Column(db.Integer,primary_key=True)
    project_id=db.Column(db.Integer,db.ForeignKey("projects.id"),nullable=False,index=True)
    name=db.Column(db.String(160),nullable=False)
    geometry=db.Column(Geometry(geometry_type="MULTIPOLYGON",srid=4326,nullable=True))
    area_hectares=db.Column(db.Float,default=0)
    latitude=db.Column(db.Float)
    longitude=db.Column(db.Float)
    status=db.Column(db.String(30),default="active")
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))
    metrics=db.relationship("Metric",backref="site",lazy=True,cascade="all, delete-orphan")
    def to_dict(self,geometry=None):
        return {"id":self.id,"project_id":self.project_id,"project_name":self.project.name,
                "name":self.name,"geometry":geometry,"area_hectares":self.area_hectares,
                "latitude":self.latitude,"longitude":self.longitude,"status":self.status}

class Metric(db.Model):
    __tablename__="metrics"
    id=db.Column(db.Integer,primary_key=True)
    site_id=db.Column(db.Integer,db.ForeignKey("sites.id"),nullable=False,index=True)
    observed_on=db.Column(db.Date,nullable=False,index=True)
    carbon_tco2e=db.Column(db.Float,default=0)
    biodiversity_index=db.Column(db.Float,default=0)
    tree_cover_pct=db.Column(db.Float,default=0)
    soil_organic_carbon_pct=db.Column(db.Float,default=0)
    rainfall_mm=db.Column(db.Float,default=0)
    def to_dict(self):
        return {"id":self.id,"observed_on":self.observed_on.isoformat(),"carbon_tco2e":self.carbon_tco2e,
                "biodiversity_index":self.biodiversity_index,"tree_cover_pct":self.tree_cover_pct,
                "soil_organic_carbon_pct":self.soil_organic_carbon_pct,"rainfall_mm":self.rainfall_mm}
