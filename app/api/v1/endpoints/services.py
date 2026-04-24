from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin
from app.models.service import Service as ServiceModel
from app.schemas.service import Service, ServiceCreate, ServiceUpdate

router = APIRouter()

@router.get("/", response_model=list[Service])
def list_services(db: Session = Depends(get_db)):
    """List all services available in the barbershop."""
    return db.query(ServiceModel).all()

@router.get("/{service_id}", response_model=Service)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific service."""
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
def create_service(
    service_in: ServiceCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Create a new service (Admin only)."""
    new_service = ServiceModel(
        name=service_in.name,
        price=service_in.price,
        duration_minutes=service_in.duration_minutes
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.patch("/{service_id}", response_model=Service)
def update_service(
    service_id: int,
    service_update: ServiceUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Update an existing service (Admin only)."""
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    update_data = service_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    """Delete a service from the catalog (Admin only)."""
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()
    return None
