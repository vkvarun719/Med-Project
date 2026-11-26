# backend/app/main.py
import os
import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

from app import models, crud, schemas
from app.database import engine, get_db
from app.barcode_utils import generate_unique_barcode, BARCODES_DIR
from app.auth import verify_station_api_key
from app.config import CORS_ORIGINS

# Initialize database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clinic Patient Measurement API",
    description="REST backend for Clinic Measurement Stations with Raspberry Pi integration",
    version="1.0.0"
)

# Enable CORS for React frontend and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory to serve barcode images
os.makedirs(BARCODES_DIR, exist_ok=True)
app.mount("/barcodes", StaticFiles(directory=BARCODES_DIR), name="barcodes")

# In-memory station session coordination state
class StationSession:
    def __init__(self):
        self.active_barcode: str | None = None
        self.live_weight: float = 0.0
        self.live_height: float = 0.0
        self.is_stable: bool = False
        self.state: str = "IDLE"  # IDLE, SCANNED, MEASURING, STABLE, SENT
        self.last_updated = datetime.datetime.utcnow()

    def reset(self):
        self.active_barcode = None
        self.live_weight = 0.0
        self.live_height = 0.0
        self.is_stable = False
        self.state = "IDLE"
        self.last_updated = datetime.datetime.utcnow()

station_session = StationSession()

# ----------------- SYSTEM ENDPOINTS -----------------
@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    try:
        # Simple query to verify database is reachable
        db.execute(models.Base.metadata.tables["patients"].select().limit(1))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "station_state": station_session.state,
        "timestamp": datetime.datetime.utcnow()
    }

# ----------------- PATIENT ENDPOINTS -----------------
@app.post("/register", response_model=schemas.PatientRegistrationResponse, status_code=status.HTTP_201_CREATED, tags=["Patients"])
def register_patient(patient_in: schemas.PatientCreate, db: Session = Depends(get_db)):
    """
    Step 1 & 2: Registers a new patient, generates an 8-character unique barcode (collision checked),
    and creates a Code128 barcode image and base64 preview for printing.
    """
    barcode_code, image_rel_path, base64_url = generate_unique_barcode(db)
    
    new_patient = crud.create_patient(
        db=db,
        name=patient_in.name,
        age=patient_in.age,
        barcode=barcode_code,
        gender=patient_in.gender,
        phone=patient_in.phone
    )

    return {
        "id": new_patient.id,
        "name": new_patient.name,
        "age": new_patient.age,
        "gender": new_patient.gender,
        "phone": new_patient.phone,
        "barcode": new_patient.barcode,
        "barcode_image_url": base64_url  # Returns self-contained base64 data URI (no IP hardcoding)
    }

@app.get("/patient/{barcode}", response_model=schemas.PatientResponse, tags=["Patients"])
def get_patient(barcode: str, db: Session = Depends(get_db)):
    """
    Fetches patient information and full measurement history (Weight, Height, BMI) by barcode.
    """
    patient = crud.get_patient_by_barcode(db, barcode=barcode.strip().upper())
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with barcode '{barcode}' not found"
        )
    return patient

@app.get("/patients", response_model=List[schemas.PatientResponse], tags=["Patients"])
def list_patients(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Lists registered patients with their latest measurements."""
    return crud.list_patients(db, skip=skip, limit=limit)

# ----------------- STATION & MEASUREMENT ENDPOINTS -----------------
@app.post("/measurements", response_model=schemas.MeasurementResponse, status_code=status.HTTP_201_CREATED, tags=["Measurements"])
def receive_measurement(
    data: schemas.MeasurementCreate,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_station_api_key)
):
    """
    Step 6, 7 & 8: Receives validated weight and height from the Raspberry Pi.
    Validates ranges, calculates BMI = weight / (height_m^2), and stores record in database.
    """
    patient = crud.get_patient_by_barcode(db, barcode=data.barcode.strip().upper())
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement rejected: Patient with barcode '{data.barcode}' does not exist"
        )

    measurement = crud.add_measurement(
        db=db,
        patient_id=patient.id,
        weight=data.weight,
        height=data.height
    )

    # Step 9: Reset the station session state for next patient
    station_session.reset()

    return measurement

@app.post("/scan", tags=["Station"])
def scan_barcode(data: schemas.ScanCreate, db: Session = Depends(get_db)):
    """
    Step 3: Signals that a barcode has been scanned at the Raspberry Pi station.
    Validates existence of patient and locks active station session.
    """
    barcode = data.barcode.strip().upper()
    patient = crud.get_patient_by_barcode(db, barcode=barcode)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown barcode: {barcode}"
        )

    station_session.active_barcode = barcode
    station_session.state = "SCANNED"
    station_session.last_updated = datetime.datetime.utcnow()

    return {
        "status": "ready",
        "barcode": barcode,
        "patient_name": patient.name,
        "patient_age": patient.age
    }

@app.post("/station/live", tags=["Station"])
def update_live_feed(
    feed: schemas.LiveFeedUpdate,
    authorized: bool = Depends(verify_station_api_key)
):
    """
    Called by Raspberry Pi during active measurement to broadcast live readings.
    """
    station_session.live_weight = feed.weight
    station_session.live_height = feed.height
    station_session.is_stable = feed.stable
    station_session.state = feed.state
    station_session.last_updated = datetime.datetime.utcnow()
    return {"message": "Live feed updated"}

@app.get("/station/live", tags=["Station"])
def get_live_feed():
    """
    Polled by React UI to show real-time station gauge and live stability status.
    """
    return {
        "active_barcode": station_session.active_barcode,
        "live_weight": station_session.live_weight,
        "live_height": station_session.live_height,
        "stable": station_session.is_stable,
        "state": station_session.state,
        "timestamp": station_session.last_updated
    }

@app.post("/station/reset", tags=["Station"])
def reset_station_session():
    """Resets the station state machine to IDLE."""
    station_session.reset()
    return {"message": "Station session reset to IDLE"}
