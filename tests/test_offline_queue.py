# tests/test_offline_queue.py
import pytest
import sqlite3
import os
import sys

sys.path.append(os.path.abspath("."))
from automation.api_client import StationApiClient

TEST_DB = "test_buffer.db"

def teardown_module():
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except OSError:
            pass

def test_offline_queue_persists_readings():
    client = StationApiClient(
        base_url="http://non-existent-domain-9999.invalid",
        api_key="test-key",
        db_path=TEST_DB
    )

    # Sending measurement to non-existent domain triggers fallback to SQLite queue
    sent = client.send_measurement(barcode="OFFL1234", weight=65.5, height=170.0)
    assert sent is False

    # Verify record was stored in SQLite database
    with sqlite3.connect(TEST_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT barcode, weight, height FROM pending_measurements WHERE barcode = 'OFFL1234'")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "OFFL1234"
        assert row[1] == 65.5
        assert row[2] == 170.0
