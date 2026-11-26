# automation/session.py
import time
import logging
from enum import Enum
from typing import Optional, Dict, Any
from automation.sensors import BaseWeightSensor, BaseHeightSensor
from automation.scanner import BarcodeScanner
from automation.stability import StabilityChecker
from automation.api_client import StationApiClient

logger = logging.getLogger("clinic_station.session")

class StationState(str, Enum):
    IDLE = "IDLE"
    SCANNED = "SCANNED"
    MEASURING = "MEASURING"
    STABLE = "STABLE"
    SENT = "SENT"
    RESET = "RESET"

class StationSessionController:
    """
    Finite State Machine orchestrating the physical measurement sequence at the clinic station.
    Cycle: IDLE -> SCANNED -> MEASURING -> STABLE -> SENT -> RESET -> IDLE
    """
    def __init__(
        self,
        weight_sensor: BaseWeightSensor,
        height_sensor: BaseHeightSensor,
        scanner: BarcodeScanner,
        stability_checker: StabilityChecker,
        api_client: StationApiClient,
        measuring_timeout_sec: float = 45.0
    ):
        self.weight_sensor = weight_sensor
        self.height_sensor = height_sensor
        self.scanner = scanner
        self.stability_checker = stability_checker
        self.api_client = api_client
        self.measuring_timeout_sec = measuring_timeout_sec

        self.state = StationState.IDLE
        self.active_barcode: Optional[str] = None
        self.patient_info: Optional[Dict[str, Any]] = None
        self.session_start_time: float = 0.0

        self.current_weight: float = 0.0
        self.current_height: float = 0.0
        self.stable_weight: Optional[float] = None
        self.stable_height: Optional[float] = None

    def _beep(self, duration_sec: float = 0.1) -> None:
        """Physical or console audio feedback."""
        logger.info("[FEEDBACK BEEP] Frequency 1kHz for %.2fs", duration_sec)

    def transition_to(self, new_state: StationState) -> None:
        logger.info("STATE TRANSITION: %s -> %s (Patient: %s)", self.state.value, new_state.value, self.active_barcode)
        self.state = new_state
        self.api_client.update_live_feed(
            weight=self.current_weight,
            height=self.current_height,
            stable=(self.state == StationState.STABLE or self.state == StationState.SENT),
            state=self.state.value
        )

    def tick(self) -> None:
        """
        Main execution tick called periodically (e.g. 5Hz to 10Hz).
        Evaluates state transitions based on scanner input, sensors, and timers.
        """
        # Read live sensors
        self.current_weight = self.weight_sensor.read_weight()
        self.current_height = self.height_sensor.read_height()

        # STATE 1: IDLE - Waiting for patient barcode scan
        if self.state == StationState.IDLE:
            scanned_code = self.scanner.poll_scan()
            if scanned_code:
                self.active_barcode = scanned_code
                self.session_start_time = time.time()
                self.stability_checker.reset()
                self._beep(0.1)
                
                # Check patient in backend (optional validation)
                info = self.api_client.check_patient_exists(scanned_code)
                self.patient_info = info
                if info:
                    logger.info("Patient identified: %s (Age: %s)", info.get("name"), info.get("age"))

                self.transition_to(StationState.SCANNED)

        # STATE 2: SCANNED - Active patient locked, waiting for person to step onto platform
        elif self.state == StationState.SCANNED:
            # Check for session timeout
            if (time.time() - self.session_start_time) > self.measuring_timeout_sec:
                logger.warning("Session timed out waiting for patient to step on scale. Resetting.")
                self.reset()
                return

            # If person steps on scale (> min weight), begin measuring
            if self.current_weight >= self.stability_checker.min_patient_weight_kg:
                self.transition_to(StationState.MEASURING)

        # STATE 3: MEASURING - Person on platform, checking stability
        elif self.state == StationState.MEASURING:
            # Check for session timeout
            if (time.time() - self.session_start_time) > self.measuring_timeout_sec:
                logger.warning("Measurement timed out before stabilizing. Resetting.")
                self.reset()
                return

            # If person stepped off completely (< min weight)
            if self.current_weight < (self.stability_checker.min_patient_weight_kg / 2.0):
                logger.debug("Platform unloaded during measurement. Waiting for patient...")
                self.stability_checker.reset()
                return

            # Add sample to stability checker
            is_stable, w, h = self.stability_checker.add_sample(self.current_weight, self.current_height)
            if is_stable and w is not None and h is not None:
                self.stable_weight = w
                self.stable_height = h
                self._beep(0.2)
                self.transition_to(StationState.STABLE)

        # STATE 4: STABLE - Stable measurement confirmed
        elif self.state == StationState.STABLE:
            if self.active_barcode and self.stable_weight and self.stable_height:
                # Transmit to backend
                self.api_client.send_measurement(
                    barcode=self.active_barcode,
                    weight=self.stable_weight,
                    height=self.stable_height
                )
                self.transition_to(StationState.SENT)

        # STATE 5: SENT - Confirmed and ready to reset
        elif self.state == StationState.SENT:
            self._beep(0.08)
            time.sleep(0.05)
            self._beep(0.08)
            self.transition_to(StationState.RESET)

        # STATE 6: RESET - Clean up session
        elif self.state == StationState.RESET:
            self.reset()

    def reset(self) -> None:
        """Cleans up the active session and returns to IDLE."""
        self.active_barcode = None
        self.patient_info = None
        self.stable_weight = None
        self.stable_height = None
        self.stability_checker.reset()
        self.transition_to(StationState.IDLE)
        logger.info("Station ready for next patient.")
