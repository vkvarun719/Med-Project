# tests/test_stability.py
import pytest
import sys
import os

sys.path.append(os.path.abspath("."))
from automation.stability import StabilityChecker

def test_stability_not_reached_before_n_samples():
    checker = StabilityChecker(sample_count=5, weight_tolerance_kg=0.2, height_tolerance_cm=0.5)
    # Add 4 steady samples (less than 5)
    for _ in range(4):
        stable, w, h = checker.add_sample(70.0, 175.0)
        assert stable is False
        assert w is None

def test_stability_reached_with_consistent_samples():
    checker = StabilityChecker(sample_count=5, weight_tolerance_kg=0.2, height_tolerance_cm=0.5)
    samples = [
        (70.05, 175.1),
        (70.10, 175.0),
        (69.95, 175.2),
        (70.00, 175.1),
        (70.05, 175.0)
    ]
    for i, (weight, height) in enumerate(samples):
        stable, w, h = checker.add_sample(weight, height)
        if i < 4:
            assert stable is False
        else:
            assert stable is True
            assert round(w, 1) == 70.0
            assert round(h, 1) == 175.1

def test_stability_rejected_when_exceeding_tolerance():
    checker = StabilityChecker(sample_count=5, weight_tolerance_kg=0.2, height_tolerance_cm=0.5)
    # Fluctuation of 0.8 kg exceeds 0.2 kg tolerance
    noisy_samples = [
        (70.0, 175.0),
        (70.8, 175.0),
        (70.1, 175.0),
        (69.9, 175.0),
        (70.5, 175.0)
    ]
    for weight, height in noisy_samples:
        stable, _, _ = checker.add_sample(weight, height)
    assert stable is False

def test_step_off_clears_buffer():
    checker = StabilityChecker(sample_count=5, min_patient_weight_kg=5.0)
    # Add 4 valid samples
    for _ in range(4):
        checker.add_sample(70.0, 175.0)
    assert len(checker.weight_buffer) == 4

    # Patient suddenly steps off (0.5 kg)
    stable, _, _ = checker.add_sample(0.5, 0.0)
    assert stable is False
    assert len(checker.weight_buffer) == 0  # Buffer cleared
