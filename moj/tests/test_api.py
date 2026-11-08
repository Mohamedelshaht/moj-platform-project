import os, tempfile
d = tempfile.mkdtemp()
os.environ.update(DATABASE_URL=f"sqlite:///{d}/t.db", ADMIN_PASSWORD="Admin-Pass-123", SECRET_KEY="k")
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
H = lambda t: {"Authorization": "Bearer " + t}
def tok(u, p):
    r = c.post("/api/login", json={"username": u, "password": p}); return r
def test_auth():
    assert tok("admin", "bad").status_code == 401
    assert c.get("/api/state").status_code == 401
def test_persist_and_roles():
    t = tok("admin", "Admin-Pass-123").json()["token"]
    assert c.put("/api/state", json={"a": 1}, headers=H(t)).status_code == 200
    assert c.get("/api/state", headers=H(t)).json()["state"] == {"a": 1}
    assert c.post("/api/users", json={"username": "viewer1", "password": "Viewer-Pass-1", "role": "اطلاع فقط"}, headers=H(t)).status_code == 200
    v = tok("viewer1", "Viewer-Pass-1").json()["token"]
    assert c.put("/api/state", json={"a": 2}, headers=H(v)).status_code == 403
    assert c.get("/api/state", headers=H(v)).json()["state"] == {"a": 1}
    assert c.get("/api/users", headers=H(v)).status_code == 403
