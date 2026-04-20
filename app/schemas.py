from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    # Intentional mass assignment vulnerability: role accepted from client input
    role: Optional[str] = "user"


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ── User Schemas ──────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserRolePatch(BaseModel):
    role: str


# ── Note Schemas ──────────────────────────────────────────────────────────────

class NoteCreate(BaseModel):
    title: str
    content: str
    # Intentional mass assignment vulnerability: owner_id accepted from client input
    owner_id: Optional[UUID] = None
    is_private: Optional[bool] = True


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteOut(BaseModel):
    id: UUID
    title: str
    content: str
    owner_id: UUID
    is_private: bool
    created_at: datetime

    class Config:
        from_attributes = True
