# tests/test_bmi.py
import pytest
import sys
import os

sys.path.append(os.path.abspath("backend"))
from app.crud import calculate_bmi

def test_bmi_standard_values():
    # Weight: 70kg, Height: 175cm -> BMI = 70 / (1.75^2) = 22.86
    assert calculate_bmi(70.0, 175.0) == 22.86

def test_bmi_underweight():
    # Weight: 45kg, Height: 170cm -> BMI = 45 / (1.70^2) = 15.57
    assert calculate_bmi(45.0, 170.0) == 15.57

def test_bmi_overweight():
    # Weight: 85kg, Height: 175cm -> BMI = 85 / (1.75^2) = 27.76
    assert calculate_bmi(85.0, 175.0) == 27.76

def test_bmi_obese():
    # Weight: 105kg, Height: 170cm -> BMI = 105 / (1.70^2) = 36.33
    assert calculate_bmi(105.0, 170.0) == 36.33

def test_bmi_edge_cases():
    # Zero or negative height should gracefully return 0.0 without ZeroDivisionError
    assert calculate_bmi(0.0, 170.0) == 0.0
    assert calculate_bmi(70.0, 0.0) == 0.0
    assert calculate_bmi(-10.0, 170.0) == 0.0
    assert calculate_bmi(70.0, -170.0) == 0.0
