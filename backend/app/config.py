# backend/app/config.py
import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

# Default fallback SQLite for zero-config local development if PostgreSQL is unset
DEFAULT_DB_URL = "sqlite:///./clinic.db"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Normalize postgres:// to postgresql:// if needed for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# API Key for securing Raspberry Pi station requests
STATION_API_KEY = os.getenv("STATION_API_KEY", "clinic-secret-pi-key-2026")

# CORS Origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Environment identifier
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
