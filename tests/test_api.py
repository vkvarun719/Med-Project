# tests/test_api.py
import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath("backend"))
from app.main import app
from app.config import STATION_API_KEY

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "station_state" in data

def test_register_and_get_patient():
    # 1. Register a new patient
    reg_payload = {
        "name": "Sarah Connor",
        "age": 29,
        "gender": "F",
        "phone": "555-0144"
    }
    reg_res = client.post("/register", json=reg_payload)
    assert reg_res.status_code == 201
    patient_data = reg_res.json()
    assert patient_data["name"] == "Sarah Connor"
    assert len(patient_data["barcode"]) == 8
    assert "data:image/png;base64," in patient_data["barcode_image_url"]

    barcode = patient_data["barcode"]

    # 2. Query patient by barcode
    get_res = client.get(f"/patient/{barcode}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["barcode"] == barcode
    assert retrieved["name"] == "Sarah Connor"
    assert isinstance(retrieved["measurements"], list)

def test_measurement_submission_and_bmi():
    # Register patient first
    reg = client.post("/register", json={"name": "Mark Watney", "age": 36, "gender": "M", "phone": "555-0188"})
    barcode = reg.json()["barcode"]

    # 1. Reject without API Key
    meas_payload = {
        "barcode": barcode,
        "weight": 75.0,
        "height": 180.0
    }
    unauthorized_res = client.post("/measurements", json=meas_payload)
    assert unauthorized_res.status_code == 401

    # 2. Accept with valid API Key
    headers = {"X-API-Key": STATION_API_KEY}
    authorized_res = client.post("/measurements", json=meas_payload, headers=headers)
    assert authorized_res.status_code == 201
    meas_data = authorized_res.json()
    assert meas_data["weight"] == 75.0
    assert meas_data["height"] == 180.0
    # BMI = 75 / (1.8^2) = 23.15
    assert meas_data["bmi"] == 23.15

    # 3. Verify measurement is reflected in patient history
    patient_res = client.get(f"/patient/{barcode}")
    measurements = patient_res.json()["measurements"]
    assert len(measurements) >= 1
    assert measurements[0]["bmi"] == 23.15

def test_station_live_and_reset():
    headers = {"X-API-Key": STATION_API_KEY}

    # Push live feed
    feed_payload = {
        "weight": 68.4,
        "height": 172.0,
        "stable": True,
        "state": "STABLE"
    }
    client.post("/station/live", json=feed_payload, headers=headers)

    # Read live feed
    get_feed = client.get("/station/live")
    assert get_feed.status_code == 200
    data = get_feed.json()
    assert data["live_weight"] == 68.4
    assert data["state"] == "STABLE"

    # Reset station
    client.post("/station/reset")
    reset_feed = client.get("/station/live")
    assert reset_feed.json()["state"] == "IDLE"
