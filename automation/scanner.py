# automation/scanner.py
import sys
import time
import select
import logging
from typing import Optional, Callable

logger = logging.getLogger("clinic_station.scanner")

class BarcodeScanner:
    """
    Modular Barcode Scanner reader.
    Handles USB HID keyboard emulation, serial interfaces, and mock simulated scans.
    Filters invalid scans and debounces rapid duplicate scans.
    """
    def __init__(self, debounce_sec: float = 2.0, mock: bool = False):
        self.debounce_sec = debounce_sec
        self.mock = mock
        self._last_barcode: Optional[str] = None
        self._last_scan_time: float = 0.0
        self._mock_queue: list[str] = []

    def queue_mock_scan(self, barcode: str) -> None:
        """Injects a simulated scan for testing."""
        self._mock_queue.append(barcode.strip().upper())

    def _is_duplicate(self, code: str) -> bool:
        now = time.time()
        if code == self._last_barcode and (now - self._last_scan_time) < self.debounce_sec:
            return True
        self._last_barcode = code
        self._last_scan_time = now
        return False

    def validate_barcode(self, raw: str) -> Optional[str]:
        """Validates that scanned input is a valid 8-character alphanumeric barcode."""
        cleaned = raw.strip().upper()
        if len(cleaned) == 8 and cleaned.isalnum():
            return cleaned
        return None

    def poll_scan(self, timeout_sec: float = 0.1) -> Optional[str]:
        """
        Polls for an incoming scan non-blockingly.
        Returns validated barcode string, or None if no scan available.
        """
        # If in mock mode, check simulated scan queue
        if self.mock and self._mock_queue:
            code = self._mock_queue.pop(0)
            if not self._is_duplicate(code):
                logger.info("Mock barcode scanned: %s", code)
                return code
            return None

        # On Linux / Raspberry Pi: Check stdin non-blockingly via select
        if hasattr(select, "select") and sys.platform != "win32":
            rlist, _, _ = select.select([sys.stdin], [], [], timeout_sec)
            if rlist:
                line = sys.stdin.readline().strip()
                validated = self.validate_barcode(line)
                if validated and not self._is_duplicate(validated):
                    logger.info("USB HID Barcode scanned: %s", validated)
                    return validated
                elif line:
                    logger.warning("Rejected invalid barcode: %s", line)

        return None
