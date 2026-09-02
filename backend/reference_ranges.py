"""Transparent reference intervals used by deterministic lab classification.

Intervals are adult-oriented demo defaults, not patient-specific medical advice.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class LabRange:
    canonical_name: str
    unit: str
    normal_low: float
    normal_high: float
    warning_low: float
    warning_high: float
    critical_low: float
    critical_high: float
    display_range: str


REFERENCE_RANGES = {
    "hemoglobin": LabRange("Hemoglobin", "g/dL", 12, 16, 10, 18, 8.5, 20, "12–16 g/dL"),
    "glucose": LabRange("Glucose", "mg/dL", 70, 140, 55, 250, 40, 300, "70–140 mg/dL"),
    "wbc": LabRange("WBC", "10³/µL", 4, 11, 2.5, 20, 1, 30, "4–11 ×10³/µL"),
    "white blood cells": LabRange("WBC", "10³/µL", 4, 11, 2.5, 20, 1, 30, "4–11 ×10³/µL"),
    "lökosit": LabRange("WBC", "10³/µL", 4, 11, 2.5, 20, 1, 30, "4–11 ×10³/µL"),
    "platelets": LabRange("Platelets", "10³/µL", 150, 450, 75, 700, 50, 1000, "150–450 ×10³/µL"),
    "trombosit": LabRange("Platelets", "10³/µL", 150, 450, 75, 700, 50, 1000, "150–450 ×10³/µL"),
    "creatinine": LabRange("Creatinine", "mg/dL", 0.6, 1.3, 0.4, 2.5, 0.2, 4, "0.6–1.3 mg/dL"),
    "sodium": LabRange("Sodium", "mEq/L", 135, 145, 125, 155, 120, 160, "135–145 mEq/L"),
    "potassium": LabRange("Potassium", "mEq/L", 3.5, 5.0, 3.0, 5.8, 2.5, 6.5, "3.5–5.0 mEq/L"),
    "cholesterol": LabRange("Cholesterol", "mg/dL", 0, 200, 0, 240, 0, 300, "Below 200 mg/dL"),
    "bilirubin": LabRange("Bilirubin", "mg/dL", 0.2, 1.2, 0.1, 3.0, 0, 5.0, "0.2–1.2 mg/dL"),
}


def normalize_test_name(test_name: str) -> str:
    return " ".join(test_name.strip().lower().split())


def lookup_range(test_name: str) -> LabRange | None:
    return REFERENCE_RANGES.get(normalize_test_name(test_name))


def units_match(provided_unit: str, expected_unit: str) -> bool:
    """Accept equivalent Unicode and caret spellings from clinical CSV exports."""
    def normalize(unit: str) -> str:
        return (unit.strip().lower().replace("³", "3").replace("^", "")
                .replace("µ", "u").replace("μ", "u").replace("/", ""))
    return normalize(provided_unit) == normalize(expected_unit)


def classify_value(lab_range: LabRange, value: float) -> str:
    """Apply critical boundaries first, then warning boundaries, then normal."""
    if value <= lab_range.critical_low or value >= lab_range.critical_high:
        return "CRITICAL"
    if value < lab_range.warning_low or value > lab_range.warning_high:
        return "WARNING"
    if lab_range.normal_low <= value <= lab_range.normal_high:
        return "NORMAL"
    return "WARNING"
