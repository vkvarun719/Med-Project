# automation/sensors/weight.py
import time
import random
import logging
from automation.sensors import BaseWeightSensor

logger = logging.getLogger("clinic_station.sensors.weight")

class HX711WeightSensor(BaseWeightSensor):
    """
    Physical driver for 4-load-cell platform using an HX711 24-bit ADC amplifier on Raspberry Pi.
    """
    def __init__(self, dout_pin: int, sck_pin: int, reference_unit: float = 420.0, offset: float = 0.0):
        self.dout_pin = dout_pin
        self.sck_pin = sck_pin
        self.reference_unit = reference_unit
        self.offset = offset
        self._hx = None

        try:
            import RPi.GPIO as GPIO
            # Configure GPIO pins
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.dout_pin, GPIO.IN)
            GPIO.setup(self.sck_pin, GPIO.OUT)
            GPIO.output(self.sck_pin, False)
            logger.info("HX711 GPIO pins initialized (DT: %d, SCK: %d)", dout_pin, sck_pin)
        except (ImportError, RuntimeError) as e:
            logger.warning("RPi.GPIO unavailable (%s). Physical sensor calls will simulate raw values.", e)

    def _read_raw(self) -> int:
        """Reads 24-bit two's complement ADC count from HX711."""
        try:
            import RPi.GPIO as GPIO
            # Wait for data ready (DOUT goes LOW)
            timeout = time.time() + 0.1
            while GPIO.input(self.dout_pin) == 1:
                if time.time() > timeout:
                    return 0
                time.sleep(0.0001)

            count = 0
            for _ in range(24):
                GPIO.output(self.sck_pin, True)
                count = (count << 1) | GPIO.input(self.dout_pin)
                GPIO.output(self.sck_pin, False)

            # 25th pulse sets channel A gain 128
            GPIO.output(self.sck_pin, True)
            GPIO.output(self.sck_pin, False)

            # Convert 24-bit 2's complement to signed int
            if count & 0x800000:
                count -= 0x1000000
            return count
        except Exception:
            return 0

    def read_weight(self) -> float:
        """Reads weight in kilograms: (raw - offset) / reference_unit."""
        raw = self._read_raw()
        if self.reference_unit == 0:
            return 0.0
        weight_kg = (raw - self.offset) / self.reference_unit
        return max(0.0, round(weight_kg, 2))

    def tare(self) -> None:
        """Averages 10 raw reads and sets offset to zero."""
        readings = [self._read_raw() for _ in range(10)]
        self.offset = sum(readings) / len(readings)
        logger.info("Tare completed. New zero offset: %.2f", self.offset)

    def calibrate(self, reference_unit: float) -> None:
        self.reference_unit = reference_unit
        logger.info("Reference unit set to: %.2f", reference_unit)


class MockWeightSensor(BaseWeightSensor):
    """
    Simulation mode weight sensor for development and laptop testing.
    Simulates a person stepping on the scale and holding steady.
    """
    def __init__(self, target_weight: float = 70.4, noise: float = 0.08):
        self.target_weight = target_weight
        self.noise = noise
        self.offset = 0.0
        self.reference_unit = 1.0
        self._is_active = True
        logger.info("MockWeightSensor initialized (Target: %.2f kg)", target_weight)

    def read_weight(self) -> float:
        if not self._is_active:
            return 0.0
        # Add slight natural fluctuation
        jitter = random.uniform(-self.noise, self.noise)
        return max(0.0, round(self.target_weight + jitter - self.offset, 2))

    def tare(self) -> None:
        self.offset = self.target_weight
        logger.info("Mock tare executed. Offset set to %.2f", self.offset)

    def calibrate(self, reference_unit: float) -> None:
        self.reference_unit = reference_unit

    def set_target(self, weight: float) -> None:
        self.target_weight = weight

    def step_off(self) -> None:
        self._is_active = False

    def step_on(self, weight: float = 70.4) -> None:
        self.target_weight = weight
        self._is_active = True


def create_weight_sensor(config: dict, mock: bool = False) -> BaseWeightSensor:
    if mock:
        return MockWeightSensor()
    
    hw_conf = config.get("hardware", {}).get("weight_sensor", {})
    try:
        import RPi.GPIO
        return HX711WeightSensor(
            dout_pin=hw_conf.get("dout_pin", 5),
            sck_pin=hw_conf.get("sck_pin", 6),
            reference_unit=hw_conf.get("reference_unit", 420.0),
            offset=hw_conf.get("offset", 0.0)
        )
    except Exception as e:
        logger.warning("Falling back to MockWeightSensor: %s", e)
        return MockWeightSensor()
