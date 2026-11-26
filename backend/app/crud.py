# backend/app/crud.py
from sqlalchemy.orm import Session
from app.models import Patient, Measurement
from typing import Optional, List

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculates Body Mass Index:
    BMI = weight (kg) / [height (m)]^2
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def create_patient(
    db: Session,
    name: str,
    age: int,
    barcode: str,
    gender: Optional[str] = None,
    phone: Optional[str] = None
) -> Patient:
    patient = Patient(
        name=name,
        age=age,
        barcode=barcode,
        gender=gender,
        phone=phone
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def get_patient_by_barcode(db: Session, barcode: str) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.barcode == barcode).first()

def get_patient_by_id(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def list_patients(db: Session, skip: int = 0, limit: int = 50) -> List[Patient]:
    return db.query(Patient).order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()

def add_measurement(
    db: Session,
    patient_id: int,
    weight: float,
    height: float
) -> Measurement:
    bmi = calculate_bmi(weight_kg=weight, height_cm=height)
    new_measurement = Measurement(
        patient_id=patient_id,
        weight=round(weight, 2),
        height=round(height, 2),
        bmi=bmi
    )
    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)
    return new_measurement

def get_measurements_by_patient_id(db: Session, patient_id: int) -> List[Measurement]:
    return db.query(Measurement).filter(
        Measurement.patient_id == patient_id
    ).order_by(Measurement.timestamp.desc()).all()
