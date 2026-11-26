# tests/test_barcode.py
import pytest
import sys
import os

sys.path.append(os.path.abspath("."))
from automation.scanner import BarcodeScanner

def test_scanner_barcode_validation():
    scanner = BarcodeScanner(mock=True)

    # Valid 8-character uppercase alphanumeric barcodes
    assert scanner.validate_barcode("A1B2C3D4") == "A1B2C3D4"
    assert scanner.validate_barcode("  e5f6g7h8  ") == "E5F6G7H8"

    # Invalid lengths or characters
    assert scanner.validate_barcode("SHORT") is None
    assert scanner.validate_barcode("TOOLONG1234") is None
    assert scanner.validate_barcode("INVALID!") is None

def test_scanner_debounces_duplicate_scans():
    scanner = BarcodeScanner(debounce_sec=1.0, mock=True)

    scanner.queue_mock_scan("CODE1234")
    scanner.queue_mock_scan("CODE1234")  # Duplicate scan

    first = scanner.poll_scan()
    assert first == "CODE1234"

    second = scanner.poll_scan()
    assert second is None  # Debounced duplicate ignored
