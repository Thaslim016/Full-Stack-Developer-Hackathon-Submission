from datetime import date
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import select
from .extensions import db
from .models import User, Project, Site, Metric
from .geo import geojson_to_db, db_to_geojson, polygon_area_hectares

api=Blueprint("api",__name__)

@api.get("/health")
def health(): return jsonify(status="ok")

@api.post("/auth/register")
def register():
    data=request.get_json() or {}
    if not all(data.get(k) for k in ("name","email","password")): return jsonify(error="name, email and password are required"),400
    if User.query.filter_by(email=data["email"].lower()).first(): return jsonify(error="email already registered"),409
    u=User(name=data["name"],email=data["email"].lower());u.set_password(data["password"]);db.session.add(u);db.session.commit()
    return jsonify(user={"id":u.id,"name":u.name,"email":u.email}),201

@api.post("/auth/login")
def login():
    data=request.get_json() or {};u=User.query.filter_by(email=(data.get("email") or "").lower()).first()
    if not u or not u.check_password(data.get("password","")): return jsonify(error="invalid credentials"),401
    return jsonify(access_token=create_access_token(identity=str(u.id)),user={"id":u.id,"name":u.name,"email":u.email})

@api.get("/projects")
@jwt_required()
def projects():
    uid=int(get_jwt_identity()); return jsonify(projects=[p.to_dict() for p in Project.query.filter_by(owner_id=uid).order_by(Project.created_at.desc()).all()])

@api.post("/projects")
@jwt_required()
def create_project():
    data=request.get_json() or {}
    if not data.get("name"): return jsonify(error="project name is required"),400
    p=Project(name=data["name"],description=data.get("description",""),owner_id=int(get_jwt_identity()))
    db.session.add(p);db.session.commit();return jsonify(project=p.to_dict()),201

@api.get("/projects/<int:project_id>")
@jwt_required()
def project(project_id):
    p=Project.query.get_or_404(project_id)
    if p.owner_id!=int(get_jwt_identity()): return jsonify(error="forbidden"),403
    return jsonify(project=p.to_dict(),sites=[s.to_dict(db_to_geojson(s.geometry)) for s in p.sites])

@api.get("/sites")
@jwt_required()
def sites():
    uid=int(get_jwt_identity())
    ss=Site.query.join(Project).filter(Project.owner_id==uid).all()
    return jsonify(sites=[s.to_dict(db_to_geojson(s.geometry)) for s in ss])

@api.post("/projects/<int:project_id>/sites")
@jwt_required()
def create_site(project_id):
    p=Project.query.get_or_404(project_id)
    if p.owner_id!=int(get_jwt_identity()): return jsonify(error="forbidden"),403
    data=request.get_json() or {};geom=data.get("geometry")
    if not data.get("name") or not geom: return jsonify(error="name and GeoJSON geometry are required"),400
    try:
        area=polygon_area_hectares(geom)
        s=Site(project_id=project_id,name=data["name"],geometry=geojson_to_db(geom),
               area_hectares=area,latitude=data.get("latitude"),longitude=data.get("longitude"))
        db.session.add(s);db.session.commit()
        return jsonify(site=s.to_dict(db_to_geojson(s.geometry))),201
    except Exception as exc:
        db.session.rollback();return jsonify(error=f"invalid geometry: {exc}"),400

@api.get("/sites/<int:site_id>")
@jwt_required()
def site(site_id):
    s=Site.query.get_or_404(site_id)
    if s.project.owner_id!=int(get_jwt_identity()): return jsonify(error="forbidden"),403
    return jsonify(site=s.to_dict(db_to_geojson(s.geometry)))

@api.get("/sites/<int:site_id>/metrics")
@jwt_required()
def site_metrics(site_id):
    s=Site.query.get_or_404(site_id)
    if s.project.owner_id!=int(get_jwt_identity()): return jsonify(error="forbidden"),403
    return jsonify(metrics=[m.to_dict() for m in Metric.query.filter_by(site_id=site_id).order_by(Metric.observed_on).all()])
