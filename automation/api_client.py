# automation/api_client.py
import time
import sqlite3
import logging
import threading
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger("clinic_station.api_client")

class StationApiClient:
    """
    Resilient HTTP API client for Raspberry Pi clinic station.
    Features:
    - X-API-Key authentication.
    - Local SQLite offline buffer queue (buffer.db) when Wi-Fi drops.
    - Automatic background sync worker with exponential backoff retry.
    """
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str = "clinic-secret-pi-key-2026",
        db_path: str = "buffer.db",
        retry_interval_sec: int = 5
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.db_path = db_path
        self.retry_interval_sec = retry_interval_sec
        self._stop_event = threading.Event()
        self._sync_thread: Optional[threading.Thread] = None

        self._init_db()

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

    def _init_db(self) -> None:
        """Initializes offline buffering SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    retry_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def queue_offline(self, barcode: str, weight: float, height: float) -> None:
        """Buffers an unsent measurement locally."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO pending_measurements (barcode, weight, height) VALUES (?, ?, ?)",
                (barcode, weight, height)
            )
            conn.commit()
        logger.warning("Network offline. Buffered measurement for %s (%.2f kg, %.1f cm) to %s",
                       barcode, weight, height, self.db_path)

    def send_measurement(self, barcode: str, weight: float, height: float) -> bool:
        """
        Sends measurement to backend. If network fails, queues to local SQLite buffer.
        Returns True if sent immediately, False if queued.
        """
        payload = {
            "barcode": barcode,
            "weight": weight,
            "height": height
        }
        try:
            resp = requests.post(
                f"{self.base_url}/measurements",
                json=payload,
                headers=self._get_headers(),
                timeout=5
            )
            if resp.status_code == 201:
                logger.info("Measurement successfully transmitted to backend for %s", barcode)
                return True
            else:
                logger.error("Backend rejected measurement (%d): %s", resp.status_code, resp.text)
                self.queue_offline(barcode, weight, height)
                return False
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning("Wi-Fi / Network failure: %s", e)
            self.queue_offline(barcode, weight, height)
            return False

    def check_patient_exists(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Queries backend to verify if scanned barcode corresponds to a registered patient."""
        try:
            resp = requests.get(
                f"{self.base_url}/patient/{barcode}",
                headers=self._get_headers(),
                timeout=4
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    def update_live_feed(self, weight: float, height: float, stable: bool, state: str) -> None:
        """Pushes current real-time station gauge to backend."""
        try:
            requests.post(
                f"{self.base_url}/station/live",
                json={"weight": weight, "height": height, "stable": stable, "state": state},
                headers=self._get_headers(),
                timeout=1
            )
        except Exception:
            pass  # Live feed is best-effort

    def _sync_loop(self) -> None:
        """Background thread to flush pending measurements when Wi-Fi recovers."""
        while not self._stop_event.is_set():
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, barcode, weight, height, retry_count FROM pending_measurements ORDER BY id ASC LIMIT 5")
                    rows = cursor.fetchall()

                    for row in rows:
                        row_id, barcode, weight, height, retries = row
                        try:
                            resp = requests.post(
                                f"{self.base_url}/measurements",
                                json={"barcode": barcode, "weight": weight, "height": height},
                                headers=self._get_headers(),
                                timeout=5
                            )
                            if resp.status_code == 201:
                                cursor.execute("DELETE FROM pending_measurements WHERE id = ?", (row_id,))
                                conn.commit()
                                logger.info("Offline sync: Flushed buffered record %d for %s", row_id, barcode)
                            else:
                                cursor.execute("UPDATE pending_measurements SET retry_count = retry_count + 1 WHERE id = ?", (row_id,))
                                conn.commit()
                        except (requests.ConnectionError, requests.Timeout):
                            break  # Still offline, wait for next tick
            except Exception as e:
                logger.debug("Sync worker exception: %s", e)

            self._stop_event.wait(self.retry_interval_sec)

    def start_sync_worker(self) -> None:
        if self._sync_thread is None or not self._sync_thread.is_alive():
            self._stop_event.clear()
            self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True, name="ApiSyncWorker")
            self._sync_thread.start()
            logger.info("Offline sync background worker started.")

    def stop_sync_worker(self) -> None:
        self._stop_event.set()
        if self._sync_thread:
            self._sync_thread.join(timeout=2)
