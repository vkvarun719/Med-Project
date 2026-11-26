# backend/app/models.py
import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    barcode = Column(String(32), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to measurements
    measurements = relationship("Measurement", back_populates="patient", cascade="all, delete-orphan", order_by="desc(Measurement.timestamp)")

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    weight = Column(Float, nullable=False)  # in kilograms
    height = Column(Float, nullable=False)  # in centimeters
    bmi = Column(Float, nullable=False)     # kg / (m^2)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # Back-reference to patient
    patient = relationship("Patient", back_populates="measurements")
