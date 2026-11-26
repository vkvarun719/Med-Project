# automation/main.py
import os
import sys
import json
import time
import signal
import logging
import argparse
from logging.handlers import RotatingFileHandler

from automation.sensors.weight import create_weight_sensor
from automation.sensors.height import create_height_sensor
from automation.scanner import BarcodeScanner
from automation.stability import StabilityChecker
from automation.api_client import StationApiClient
from automation.session import StationSessionController

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "clinic-station.log")

def setup_logging():
    logger = logging.getLogger("clinic_station")
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"))
    logger.addHandler(console_handler)

    # Rotating file handler (5MB per file, max 3 backups)
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"))
    logger.addHandler(file_handler)

    return logger

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Clinic Patient Measurement Station - Raspberry Pi Daemon")
    parser.add_argument("--mock", action="store_true", help="Run in mock/simulation mode (no physical GPIO hardware needed)")
    parser.add_argument("--tare", action="store_true", help="Zero the scale platform and save offset to config.json")
    parser.add_argument("--calibrate-weight", type=float, help="Set reference unit for weight sensor calibration")
    parser.add_argument("--calibrate-height", type=float, help="Set stadiometer ceiling distance (cm) for height calibration")
    args = parser.parse_args()

    logger = setup_logging()
    logger.info("Starting Clinic Station Daemon (PID: %d)", os.getpid())

    config = load_config()

    # Handle calibration commands
    if args.tare:
        sensor = create_weight_sensor(config, mock=False)
        sensor.tare()
        config["hardware"]["weight_sensor"]["offset"] = getattr(sensor, "offset", 0.0)
        save_config(config)
        logger.info("Tare completed and saved to config.json. Exiting.")
        return

    if args.calibrate_weight is not None:
        config["hardware"]["weight_sensor"]["reference_unit"] = args.calibrate_weight
        save_config(config)
        logger.info("Weight reference unit updated to %.2f. Exiting.", args.calibrate_weight)
        return

    if args.calibrate_height is not None:
        config["hardware"]["height_sensor"]["stadiometer_ceiling_cm"] = args.calibrate_height
        save_config(config)
        logger.info("Stadiometer ceiling height updated to %.1f cm. Exiting.", args.calibrate_height)
        return

    # Check environment flag MOCK_MODE
    is_mock = args.mock or os.getenv("MOCK_MODE", "false").lower() in ("true", "1")
    if is_mock:
        logger.warning(">>> RUNNING IN MOCK / SIMULATION MODE <<<")

    # Initialize components
    weight_sensor = create_weight_sensor(config, mock=is_mock)
    height_sensor = create_height_sensor(config, mock=is_mock)
    scanner = BarcodeScanner(mock=is_mock)

    stab_conf = config.get("stability", {})
    stability_checker = StabilityChecker(
        sample_count=stab_conf.get("sample_count", 5),
        weight_tolerance_kg=stab_conf.get("weight_tolerance_kg", 0.2),
        height_tolerance_cm=stab_conf.get("height_tolerance_cm", 0.5),
        min_patient_weight_kg=stab_conf.get("min_patient_weight_kg", 5.0)
    )

    api_client = StationApiClient(
        base_url=config.get("api_base_url", "http://localhost:8000"),
        api_key=config.get("station_api_key", "clinic-secret-pi-key-2026"),
        db_path=config.get("offline_db_path", "buffer.db"),
        retry_interval_sec=config.get("sync", {}).get("retry_interval_sec", 5)
    )
    api_client.start_sync_worker()

    controller = StationSessionController(
        weight_sensor=weight_sensor,
        height_sensor=height_sensor,
        scanner=scanner,
        stability_checker=stability_checker,
        api_client=api_client
    )

    # Graceful shutdown handler
    running = True
    def shutdown_signal(sig, frame):
        nonlocal running
        logger.info("Shutdown signal received (%s). Cleaning up...", sig)
        running = False

    signal.signal(signal.SIGINT, shutdown_signal)
    signal.signal(signal.SIGTERM, shutdown_signal)

    interval = stab_conf.get("sample_interval_sec", 0.2)
    logger.info("Clinic Station operational. Waiting for patient scan...")

    try:
        while running:
            controller.tick()
            time.sleep(interval)
    finally:
        api_client.stop_sync_worker()
        logger.info("Clinic Station stopped cleanly.")

if __name__ == "__main__":
    main()
