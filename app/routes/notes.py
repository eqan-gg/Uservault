from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Note
from app.schemas import NoteCreate, NoteUpdate, NoteOut
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/v1/notes", tags=["Notes"])

_bearer = HTTPBearer()


@router.get("", response_model=list[NoteOut])
def list_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Note).filter(Note.owner_id == current_user.id).all()


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    body: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional mass assignment vulnerability: if owner_id supplied in body, use it directly
    owner_id = body.owner_id if body.owner_id is not None else current_user.id

    note = Note(
        title=body.title,
        content=body.content,
        owner_id=owner_id,
        is_private=body.is_private,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteOut)
def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional BOLA: no ownership check — any authenticated user can read any note
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: str,
    body: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional BOLA: no ownership check — any authenticated user can update any note
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if body.title is not None:
        note.title = body.title
    if body.content is not None:
        note.content = body.content

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Intentional BOLA: no ownership check — any authenticated user can delete any note
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()
