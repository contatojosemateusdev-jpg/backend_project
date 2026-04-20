from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_admin
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate

router = APIRouter()

@router.get("/me", response_model=User)
def get_me(current_user: UserModel = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return current_user

@router.patch("/me", response_model=User)
def update_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update the current user's profile."""
    db_user = current_user
    for field, value in user_update.model_dump(exclude_unset=True).items():
        if field == "password":
            from app.core.security import get_password_hash
            db_user.hashed_password = get_password_hash(value)
        else:
            setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=list[User])
def list_users(
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    """List all users (Admin only)."""
    return db.query(UserModel).all()

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(get_current_admin)
):
    """Delete a user (Admin only)."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None
