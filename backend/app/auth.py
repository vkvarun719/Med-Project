# backend/app/auth.py
from fastapi import Header, HTTPException, status
from app.config import STATION_API_KEY

def verify_station_api_key(x_api_key: str = Header(None)):
    """
    Dependency to verify incoming requests from the clinic station Raspberry Pi.
    Ensures that only authorized hardware units can post measurements.
    """
    if not STATION_API_KEY:
        return True  # If no key configured in dev, allow

    if not x_api_key or x_api_key != STATION_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Station API Key (X-API-Key)"
        )
    return True
