# backend/app/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import datetime

# ----------------- PATIENT SCHEMAS -----------------
class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full patient name")
    age: int = Field(..., ge=0, le=130, description="Age in years")
    gender: Optional[str] = Field(None, max_length=10, description="Gender (M/F/O)")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number")

    @field_validator("name")
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be blank")
        return cleaned

class MeasurementResponse(BaseModel):
    id: int
    patient_id: int
    weight: float
    height: float
    bmi: float
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: Optional[str] = None
    phone: Optional[str] = None
    barcode: str
    created_at: datetime.datetime
    measurements: List[MeasurementResponse] = []

    class Config:
        from_attributes = True

class PatientRegistrationResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: Optional[str] = None
    phone: Optional[str] = None
    barcode: str
    barcode_image_url: str

# ----------------- MEASUREMENT SCHEMAS -----------------
class MeasurementCreate(BaseModel):
    barcode: str = Field(..., min_length=4, max_length=32, description="Patient 8-char barcode")
    weight: float = Field(..., ge=1.0, le=350.0, description="Weight in kg (1.0 to 350.0)")
    height: float = Field(..., ge=30.0, le=250.0, description="Height in cm (30.0 to 250.0)")

class ScanCreate(BaseModel):
    barcode: str = Field(..., min_length=1, description="Scanned barcode string")

class LiveFeedUpdate(BaseModel):
    weight: float = 0.0
    height: float = 0.0
    stable: bool = False
    state: str = "IDLE"
