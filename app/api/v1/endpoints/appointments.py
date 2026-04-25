from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
from app.api.deps import get_db, get_current_user, get_current_admin
from app.models.appointment import Appointment as AppointmentModel, AppointmentStatus
from app.models.professional import Professional as ProfessionalModel, ProfessionalWorkingHour as WorkingHourModel
from app.models.service import Service as ServiceModel
from app.schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate

router = APIRouter()

def check_availability(db: Session, professional_id: int, start_time: datetime, end_time: datetime):
    """Check if the professional is available in the given time range, including working hours."""
    # 1. Check if it falls within the professional's working hours
    day_of_week = start_time.weekday()
    start_t = start_time.time()
    end_t = end_time.time()

    # Note: This logic assumes the appointment starts and ends on the same calendar day.
    # For most booking systems (barbershops), this is a standard constraint.
    working_slots = db.query(WorkingHourModel).filter(
        WorkingHourModel.professional_id == professional_id,
        WorkingHourModel.day_of_week == day_of_week
    ).all()

    if not working_slots:
        return False

    # The appointment must fit entirely within at least one working slot
    is_within_working_hours = any(
        slot.start_time <= start_t and slot.end_time >= end_t
        for slot in working_slots
    )

    if not is_within_working_hours:
        return False

    # 2. Check for overlapping scheduled appointments
    overlap = db.query(AppointmentModel).filter(
        AppointmentModel.professional_id == professional_id,
        AppointmentModel.status == AppointmentStatus.SCHEDULED,
        AppointmentModel.start_time < end_time,
        AppointmentModel.end_time > start_time
    ).first()

    return overlap is None

@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_in: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Book a new appointment (Client)."""
    # 1. Validate Service
    service = db.query(ServiceModel).filter(ServiceModel.id == appointment_in.service_id, ServiceModel.is_active == True).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found or inactive")

    # 2. Validate Professional
    professional = db.query(ProfessionalModel).filter(ProfessionalModel.id == appointment_in.professional_id, ProfessionalModel.is_active == True).first()
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found or inactive")

    # 3. Calculate end time
    start_time = appointment_in.start_time
    end_time = start_time + timedelta(minutes=service.duration_minutes)

    # 4. Check availability
    if not check_availability(db, appointment_in.professional_id, start_time, end_time):
        raise HTTPException(status_code=400, detail="Professional is not available at this time or outside working hours")

    # 5. Create appointment
    new_appointment = AppointmentModel(
        client_id=current_user.id,
        professional_id=appointment_in.professional_id,
        service_id=appointment_in.service_id,
        start_time=start_time,
        end_time=end_time,
        status=AppointmentStatus.SCHEDULED
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

@router.get("/", response_model=list[Appointment])
def list_appointments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """List appointments (Client sees theirs, Admin sees all)."""
    # Check if user is admin
    if current_user.role.value == "admin":
        return db.query(AppointmentModel).all()

    return db.query(AppointmentModel).filter(AppointmentModel.client_id == current_user.id).all()

@router.patch("/{app_id}", response_model=Appointment)
def update_appointment(
    app_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Update an appointment (Admin or the client who owns it)."""
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == app_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.id != appointment.client_id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this appointment")

    if appointment_update.status:
        appointment.status = appointment_update.status

    if appointment_update.start_time:
        # Re-calculate end time based on the service
        service = db.query(ServiceModel).filter(ServiceModel.id == appointment.service_id).first()
        new_start = appointment_update.start_time
        new_end = new_start + timedelta(minutes=service.duration_minutes)

        if not check_availability(db, appointment.professional_id, new_start, new_end):
            raise HTTPException(status_code=400, detail="Professional is not available at this new time or outside working hours")

        appointment.start_time = new_start
        appointment.end_time = new_end

    db.commit()
    db.refresh(appointment)
    return appointment

@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_appointment(
    app_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Cancel an appointment (Soft delete via status)."""
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == app_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.id != appointment.client_id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    return None
