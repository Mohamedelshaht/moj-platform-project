import os, secrets, json, logging
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, Header, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt, jwt

log = logging.getLogger("moj")
DB = os.getenv("DATABASE_URL", "sqlite:///./moj.db").replace("postgres://", "postgresql://", 1)
SECRET = os.getenv("SECRET_KEY") or secrets.token_hex(32)
ROLES = ["مدير النظام", "الإدارة المركزية", "مسؤول قطاع", "مسؤول محافظة/مقر", "مسؤول مشروعات", "مسؤول شكاوى", "مسؤول أزمات", "اطلاع فقط"]
engine = create_engine(DB, connect_args={"check_same_thread": False} if DB.startswith("sqlite") else {})
Session = sessionmaker(bind=engine)
Base = declarative_base()
now = lambda: datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(60), unique=True, nullable=False)
    pw = Column(String(100), nullable=False)
    role = Column(String(40), nullable=False)
    active = Column(Boolean, default=True)

class State(Base):
    __tablename__ = "state"
    id = Column(Integer, primary_key=True)
    data = Column(Text, nullable=False)
    updated = Column(DateTime(timezone=True), default=now)

class Audit(Base):
    __tablename__ = "audit"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime(timezone=True), default=now)
    user = Column(String(60))
    action = Column(String(200))

Base.metadata.create_all(engine)
hp = lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def init():
    with Session() as db:
        if not db.query(User).count():
            pw = os.getenv("ADMIN_PASSWORD")
            if not pw:
                pw = secrets.token_urlsafe(12)
                log.warning("ADMIN_PASSWORD غير مضبوط. كلمة مرور admin المؤقتة: %s", pw)
            db.add(User(username="admin", pw=hp(pw), role=ROLES[0]))
            db.commit()
init()

def get_db():
    with Session() as db:
        yield db

def me(authorization: str = Header(None), db=Depends(get_db)):
    try:
        p = jwt.decode(authorization.split()[1], SECRET, algorithms=["HS256"])
        u = db.query(User).filter_by(username=p["sub"], active=True).first()
    except Exception:
        u = None
    if not u:
        raise HTTPException(401, "غير مصرح")
    return u

def audit(db, u, a):
    db.add(Audit(user=u, action=a)); db.commit()

app = FastAPI(title="منصة العقل الرقمي - وزارة العدل")

class Login(BaseModel):
    username: str = Field(max_length=60)
    password: str = Field(max_length=64)

class NewUser(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    password: str = Field(min_length=10, max_length=64)
    role: str

@app.get("/api/health")
def health(): return {"ok": True}

@app.post("/api/login")
def login(b: Login, db=Depends(get_db)):
    u = db.query(User).filter_by(username=b.username, active=True).first()
    if not u or not bcrypt.checkpw(b.password.encode(), u.pw.encode()):
        raise HTTPException(401, "بيانات الدخول غير صحيحة")
    tok = jwt.encode({"sub": u.username, "exp": now() + timedelta(hours=8)}, SECRET, algorithm="HS256")
    audit(db, u.username, "تسجيل دخول")
    return {"token": tok, "username": u.username, "role": u.role}

@app.get("/api/me")
def whoami(u=Depends(me)): return {"username": u.username, "role": u.role}

@app.get("/api/state")
def get_state(u=Depends(me), db=Depends(get_db)):
    s = db.get(State, 1)
    return {"state": json.loads(s.data) if s else None}

@app.put("/api/state")
def put_state(data: dict = Body(...), u=Depends(me), db=Depends(get_db)):
    if u.role == ROLES[-1]:
        raise HTTPException(403, "صلاحية الاطلاع فقط")
    raw = json.dumps(data, ensure_ascii=False)
    if len(raw) > 3_000_000:
        raise HTTPException(413, "حجم البيانات كبير")
    s = db.get(State, 1)
    if s: s.data, s.updated = raw, now()
    else: db.add(State(id=1, data=raw))
    db.commit(); audit(db, u.username, "حفظ البيانات")
    return {"ok": True}

@app.delete("/api/state")
def reset_state(u=Depends(me), db=Depends(get_db)):
    if u.role != ROLES[0]: raise HTTPException(403, "للمدير فقط")
    db.query(State).delete(); db.commit(); audit(db, u.username, "إعادة ضبط البيانات")
    return {"ok": True}

@app.get("/api/users")
def users(u=Depends(me), db=Depends(get_db)):
    if u.role != ROLES[0]: raise HTTPException(403, "للمدير فقط")
    return [{"username": x.username, "role": x.role, "active": x.active} for x in db.query(User)]

@app.post("/api/users")
def add_user(b: NewUser, u=Depends(me), db=Depends(get_db)):
    if u.role != ROLES[0]: raise HTTPException(403, "للمدير فقط")
    if b.role not in ROLES: raise HTTPException(422, "دور غير معروف")
    if db.query(User).filter_by(username=b.username).first(): raise HTTPException(409, "الاسم مستخدم")
    db.add(User(username=b.username, pw=hp(b.password), role=b.role)); db.commit()
    audit(db, u.username, "إنشاء مستخدم " + b.username)
    return {"ok": True}

@app.get("/api/audit")
def get_audit(u=Depends(me), db=Depends(get_db)):
    if u.role != ROLES[0]: raise HTTPException(403, "للمدير فقط")
    return [{"ts": str(a.ts), "user": a.user, "action": a.action} for a in db.query(Audit).order_by(Audit.id.desc()).limit(200)]

app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static"), html=True), name="static")
