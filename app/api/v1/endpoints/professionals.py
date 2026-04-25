from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin
from app.models.professional import Professional as ProfessionalModel, ProfessionalWorkingHour as WorkingHourModel
from app.models.user import User as UserModel
from app.schemas.professional import Professional, ProfessionalCreate, ProfessionalUpdate, WorkingHour, WorkingHourCreate
from typing import List

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
    if professional_in.user_id:
        user_exists = db.query(UserModel).filter(UserModel.id == professional_in.user_id).first()
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The specified user_id does not exist"
            )

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
    """Deactivate a professional from the catalog (Admin only)."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    professional.is_active = False
    db.commit()
    return None

@router.get("/{prof_id}/working-hours", response_model=List[WorkingHour])
def get_working_hours(prof_id: int, db: Session = Depends(get_db)):
    """Get all working hour slots for a professional."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    return professional.working_hours

@router.post("/{prof_id}/working-hours", response_model=List[WorkingHour], status_code=status.HTTP_201_CREATED)
def create_working_hours(
    prof_id: int,
    working_hours_in: List[WorkingHourCreate],
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Add working hour slots for a professional (Admin only)."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    new_slots = []
    for slot in working_hours_in:
        if slot.start_time >= slot.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Start time {slot.start_time} must be before end time {slot.end_time}"
            )

        db_slot = WorkingHourModel(
            professional_id=prof_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time
        )
        new_slots.append(db_slot)

    db.add_all(new_slots)
    db.commit()

    # Return all slots for the professional after adding
    return db.query(WorkingHourModel).filter(WorkingHourModel.professional_id == prof_id).all()

@router.put("/{prof_id}/working-hours", response_model=List[WorkingHour])
def replace_working_hours(
    prof_id: int,
    working_hours_in: List[WorkingHourCreate],
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Replace all working hour slots for a professional (Admin only)."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    # Delete all existing slots
    db.query(WorkingHourModel).filter(WorkingHourModel.professional_id == prof_id).delete()

    # Add new slots
    new_slots = []
    for slot in working_hours_in:
        if slot.start_time >= slot.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Start time {slot.start_time} must be before end time {slot.end_time}"
            )

        db_slot = WorkingHourModel(
            professional_id=prof_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time
        )
        new_slots.append(db_slot)

    db.add_all(new_slots)
    db.commit()
    return db.query(WorkingHourModel).filter(WorkingHourModel.professional_id == prof_id).all()

@router.delete("/{prof_id}/working-hours", status_code=status.HTTP_204_NO_CONTENT)
def delete_working_hours(
    prof_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Clear all working hour slots for a professional (Admin only)."""
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == prof_id).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    db.query(WorkingHourModel).filter(WorkingHourModel.professional_id == prof_id).delete()
    db.commit()
    return None
