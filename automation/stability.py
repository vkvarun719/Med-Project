# automation/stability.py
import collections
import logging
from typing import Tuple, Optional

logger = logging.getLogger("clinic_station.stability")

class StabilityChecker:
    """
    Evaluates sensor readings on the Raspberry Pi to determine when weight
    and height have settled into a stable, valid measurement.

    Conditions for Stability:
    1. Both weight and height buffers have accumulated N consecutive samples.
    2. Span of weight buffer (max - min) <= weight_tolerance_kg.
    3. Span of height buffer (max - min) <= height_tolerance_cm.
    4. Average weight is above min_patient_weight_kg (prevents empty platform stability).
    """
    def __init__(
        self,
        sample_count: int = 5,
        weight_tolerance_kg: float = 0.2,
        height_tolerance_cm: float = 0.5,
        min_patient_weight_kg: float = 5.0
    ):
        self.sample_count = sample_count
        self.weight_tolerance_kg = weight_tolerance_kg
        self.height_tolerance_cm = height_tolerance_cm
        self.min_patient_weight_kg = min_patient_weight_kg

        self.weight_buffer = collections.deque(maxlen=self.sample_count)
        self.height_buffer = collections.deque(maxlen=self.sample_count)

    def reset(self) -> None:
        """Clears all sample buffers."""
        self.weight_buffer.clear()
        self.height_buffer.clear()

    def add_sample(self, weight: float, height: float) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Adds a new (weight, height) reading pair.
        Returns: (is_stable, stable_weight, stable_height)
        """
        # If weight drops significantly (patient stepping off), immediately clear
        if weight < (self.min_patient_weight_kg / 2.0) and len(self.weight_buffer) > 0:
            logger.debug("Patient stepped off or platform unloaded. Resetting stability buffer.")
            self.reset()
            return False, None, None

        self.weight_buffer.append(weight)
        self.height_buffer.append(height)

        # Buffer must be fully populated
        if len(self.weight_buffer) < self.sample_count:
            return False, None, None

        weight_span = max(self.weight_buffer) - min(self.weight_buffer)
        height_span = max(self.height_buffer) - min(self.height_buffer)
        avg_weight = sum(self.weight_buffer) / len(self.weight_buffer)
        avg_height = sum(self.height_buffer) / len(self.height_buffer)

        # Check tolerances
        if (
            weight_span <= self.weight_tolerance_kg
            and height_span <= self.height_tolerance_cm
            and avg_weight >= self.min_patient_weight_kg
            and avg_height > 20.0
        ):
            stable_w = round(avg_weight, 2)
            stable_h = round(avg_height, 1)
            logger.info("Stability reached! W: %.2f kg (span: %.2f), H: %.1f cm (span: %.1f)",
                        stable_w, weight_span, stable_h, height_span)
            return True, stable_w, stable_h

        return False, None, None
