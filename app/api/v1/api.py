from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, services, professionals, appointments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(services.router, prefix="/services", tags=["Services"])
api_router.include_router(professionals.router, prefix="/professionals", tags=["Professionals"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
