from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import bcrypt

from app.database import engine, SessionLocal, Base
from app.models import User, Note
from app.routes import auth, notes, users, upload, admin


def _hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _seed_data(db: Session):
    """Seed admin user, regular user, and demo notes if the DB is empty."""
    if db.query(User).count() > 0:
        return  # Already seeded

    # ── Seed admin ────────────────────────────────────────────────────────────
    admin_user = User(
        username="admin",
        email="admin@uservault.com",
        password_hash=_hash("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(admin_user)
    db.flush()

    # ── Seed regular user ─────────────────────────────────────────────────────
    john = User(
        username="john",
        email="john@uservault.com",
        password_hash=_hash("john123"),
        role="user",
        is_active=True,
    )
    db.add(john)
    db.flush()

    # ── Seed 3 notes owned by john (BOLA demo surface) ────────────────────────
    notes_data = [
        Note(
            title="My Secret Recipe",
            content="Step 1: Add two cups of flour. Step 2: Mix with milk. Step 3: Bake at 180°C.",
            owner_id=john.id,
            is_private=True,
        ),
        Note(
            title="Weekend Plans",
            content="Visit the lake on Saturday. Buy groceries on Sunday morning.",
            owner_id=john.id,
            is_private=True,
        ),
        Note(
            title="Work Ideas",
            content="Propose the new dashboard feature to the team. Schedule sync with design.",
            owner_id=john.id,
            is_private=False,
        ),
    ]
    db.add_all(notes_data)
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        _seed_data(db)
    finally:
        db.close()
    yield


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="UserVault API",
    description="A user and notes management REST API",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(users.router)
app.include_router(upload.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "api": "UserVault API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
