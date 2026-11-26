# automation/sensors/__init__.py
"""
Sensor abstraction layer for Clinic Patient Measurement System
Supports real Raspberry Pi GPIO and Mock/Simulation hardware mode
"""
from abc import ABC, abstractmethod

class BaseWeightSensor(ABC):
    @abstractmethod
    def read_weight(self) -> float:
        """Returns weight in kilograms."""
        pass

    @abstractmethod
    def tare(self) -> None:
        """Zeroes the scale."""
        pass

    @abstractmethod
    def calibrate(self, reference_unit: float) -> None:
        """Sets the calibration multiplier."""
        pass


class BaseHeightSensor(ABC):
    @abstractmethod
    def read_height(self) -> float:
        """Returns patient height in centimeters."""
        pass

    @abstractmethod
    def calibrate_ceiling(self, ceiling_cm: float) -> None:
        """Calibrates total overhead stadiometer distance."""
        pass
