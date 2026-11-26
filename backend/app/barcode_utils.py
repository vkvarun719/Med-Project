# backend/app/barcode_utils.py
import os
import uuid
import base64
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from sqlalchemy.orm import Session
from app.models import Patient

BARCODES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "barcodes")
os.makedirs(BARCODES_DIR, exist_ok=True)

def generate_unique_barcode(db: Session, max_attempts: int = 10) -> tuple[str, str, str]:
    """
    Generates a unique 8-character Code128 barcode.
    Guarantees no collision with existing patient barcodes in the database.
    Returns: (barcode_text, relative_image_path, base64_data_url)
    """
    for _ in range(max_attempts):
        # Generate 8-character uppercase hex code
        code = uuid.uuid4().hex[:8].upper()

        # Check collision in database
        existing = db.query(Patient).filter(Patient.barcode == code).first()
        if not existing:
            # Generate Code128 barcode
            code128 = barcode.get("code128", code, writer=ImageWriter())
            
            # Save PNG to disk
            filepath = os.path.join(BARCODES_DIR, code)
            saved_path = code128.save(filepath)

            # Generate base64 data URI for instant client-side rendering
            buffer = BytesIO()
            code128.write(buffer)
            b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            base64_url = f"data:image/png;base64,{b64_str}"

            return code, f"/barcodes/{code}.png", base64_url

    raise RuntimeError("Failed to generate a unique barcode after multiple attempts")
