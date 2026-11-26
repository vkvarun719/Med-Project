# automation/sensors/height.py
import time
import random
import logging
from automation.sensors import BaseHeightSensor

logger = logging.getLogger("clinic_station.sensors.height")

class HCSR04HeightSensor(BaseHeightSensor):
    """
    Physical driver for overhead HC-SR04 ultrasonic stadiometer on Raspberry Pi.
    Measures distance from top stadiometer bar to patient head, and computes:
    Patient Height = Stadiometer Ceiling - Measured Head Distance.
    """
    def __init__(self, trigger_pin: int, echo_pin: int, stadiometer_ceiling_cm: float = 220.0, offset_cm: float = 0.0):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.stadiometer_ceiling_cm = stadiometer_ceiling_cm
        self.offset_cm = offset_cm

        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trigger_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trigger_pin, False)
            time.sleep(0.05)  # Allow settle time
            logger.info("HC-SR04 GPIO initialized (TRIG: %d, ECHO: %d)", trigger_pin, echo_pin)
        except (ImportError, RuntimeError) as e:
            logger.warning("RPi.GPIO unavailable (%s). Height sensor will return default baseline.", e)

    def _measure_distance_cm(self) -> float:
        """Fires 10us ultrasonic pulse and measures echo pulse duration."""
        try:
            import RPi.GPIO as GPIO
            # Send 10us trigger pulse
            GPIO.output(self.trigger_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trigger_pin, False)

            pulse_start = time.time()
            pulse_end = time.time()
            timeout = pulse_start + 0.04  # 40ms timeout (max ~6m)

            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()
                if pulse_start > timeout:
                    return -1.0

            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()
                if pulse_end > timeout:
                    return -1.0

            # Sound speed in air: 34300 cm/s
            duration = pulse_end - pulse_start
            distance_cm = (duration * 34300.0) / 2.0
            return distance_cm
        except Exception as e:
            logger.debug("Ultrasonic ping failed: %s", e)
            return -1.0

    def read_height(self) -> float:
        dist = self._measure_distance_cm()
        if dist < 0 or dist > self.stadiometer_ceiling_cm:
            # No object detected below sensor, or reading error
            return 0.0

        patient_height = self.stadiometer_ceiling_cm - dist + self.offset_cm
        return max(0.0, round(patient_height, 1))

    def calibrate_ceiling(self, ceiling_cm: float) -> None:
        self.stadiometer_ceiling_cm = ceiling_cm
        logger.info("Stadiometer ceiling height calibrated to: %.1f cm", ceiling_cm)


class MockHeightSensor(BaseHeightSensor):
    """
    Simulation mode height sensor for development and laptop testing.
    """
    def __init__(self, target_height_cm: float = 175.2, noise: float = 0.2):
        self.target_height_cm = target_height_cm
        self.noise = noise
        self.ceiling_cm = 220.0
        self._is_active = True
        logger.info("MockHeightSensor initialized (Target: %.1f cm)", target_height_cm)

    def read_height(self) -> float:
        if not self._is_active:
            return 0.0
        jitter = random.uniform(-self.noise, self.noise)
        return max(0.0, round(self.target_height_cm + jitter, 1))

    def calibrate_ceiling(self, ceiling_cm: float) -> None:
        self.ceiling_cm = ceiling_cm

    def set_target(self, height_cm: float) -> None:
        self.target_height_cm = height_cm

    def step_off(self) -> None:
        self._is_active = False

    def step_on(self, height_cm: float = 175.2) -> None:
        self.target_height_cm = height_cm
        self._is_active = True


def create_height_sensor(config: dict, mock: bool = False) -> BaseHeightSensor:
    if mock:
        return MockHeightSensor()

    hw_conf = config.get("hardware", {}).get("height_sensor", {})
    try:
        import RPi.GPIO
        return HCSR04HeightSensor(
            trigger_pin=hw_conf.get("trigger_pin", 23),
            echo_pin=hw_conf.get("echo_pin", 24),
            stadiometer_ceiling_cm=hw_conf.get("stadiometer_ceiling_cm", 220.0),
            offset_cm=hw_conf.get("offset_cm", 0.0)
        )
    except Exception as e:
        logger.warning("Falling back to MockHeightSensor: %s", e)
        return MockHeightSensor()
