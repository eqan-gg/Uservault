from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Note
from app.schemas import UserOut, UserRolePatch
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

_bearer = HTTPBearer()


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional broken access control: no admin role check — any authenticated user can see stats
    total_users = db.query(User).count()
    total_notes = db.query(Note).count()
    active_users = db.query(User).filter(User.is_active == True).count()

    return {
        "total_users": total_users,
        "total_notes": total_notes,
        "active_users": active_users,
    }


@router.patch("/users/{user_id}", response_model=UserOut)
def patch_user_role(
    user_id: str,
    body: UserRolePatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional BOLA + broken access control: no admin check, any authenticated user can change any user's role
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = body.role
    db.commit()
    db.refresh(user)
    return user
