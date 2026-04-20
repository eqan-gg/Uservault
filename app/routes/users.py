from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

_bearer = HTTPBearer()


@router.get("", response_model=list[UserOut])
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional broken access control: no admin role check — any authenticated user can list all users
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional BOLA: any authenticated user can fetch any user's data by UUID
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional broken access control: no admin check — any authenticated user can delete any user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
