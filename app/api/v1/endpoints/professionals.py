from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin
from app.models.professional import Professional as ProfessionalModel
from app.schemas.professional import Professional, ProfessionalCreate, ProfessionalUpdate

router = APIRouter()

@router.get("/", response_model=list[Professional])
def list_professionals(db: Session = Depends(get_db)):
    """List all professionals in the barbershop."""
    return db.query(ProfessionalModel).all()

@router.get("/{prof_id}", response_model=Professional)
def get_professional(prof_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific professional."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    return professional

@router.post("/", response_model=Professional, status_code=status.HTTP_201_CREATED)
def create_professional(
    professional_in: ProfessionalCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Create a new professional profile (Admin only)."""
    new_prof = ProfessionalModel(
        name=professional_in.name,
        specialty=professional_in.specialty,
        is_active=professional_in.is_active,
        user_id=professional_in.user_id
    )
    db.add(new_prof)
    db.commit()
    db.refresh(new_prof)
    return new_prof

@router.patch("/{prof_id}", response_model=Professional)
def update_professional(
    prof_id: int,
    professional_update: ProfessionalUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Update an existing professional's profile (Admin only)."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    update_data = professional_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(professional, field, value)

    db.commit()
    db.refresh(professional)
    return professional

@router.delete("/{prof_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professional(
    prof_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Delete a professional from the catalog (Admin only)."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    db.delete(professional)
    db.commit()
    return None
