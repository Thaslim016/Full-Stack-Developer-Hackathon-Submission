import pytest
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture()
def client():
    app=create_app({"TESTING":True,"SQLALCHEMY_DATABASE_URI":"sqlite:///:memory:","JWT_SECRET_KEY":"test"})
    with app.app_context():
        db.create_all()
        u=User(name="Test",email="test@example.com");u.set_password("password123");db.session.add(u);db.session.commit()
    return app.test_client()

def token(client):
    r=client.post("/api/auth/login",json={"email":"test@example.com","password":"password123"})
    return r.get_json()["access_token"]

def test_auth_and_project(client):
    t=token(client)
    r=client.post("/api/projects",json={"name":"Test project"},headers={"Authorization":f"Bearer {t}"})
    assert r.status_code==201
    assert r.get_json()["project"]["name"]=="Test project"
