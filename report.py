"""Formats calibration and cross-check results into a scorecard."""

from __future__ import annotations

from calibrate import CalibrationReport
from cross_check import CrossCheckReport


def build_report(calibration: CalibrationReport, cross: CrossCheckReport | None = None) -> str:
    lines = ["# Judge Calibration Scorecard", "", "## Agreement with human labels (Cohen's kappa)"]
    lines += ["| Dimension | Kappa |", "|---|---|"]
    lines += [f"| {dim} | {kappa:.2f} |" for dim, kappa in calibration.kappa_by_dimension.items()]

    lines += [
        "",
        "## Bias checks",
        f"- Position bias (should be ~0): {calibration.position_bias:.2f}",
        f"- Verbosity bias (should be ~0): {calibration.verbosity_bias:.2f}",
    ]

    if cross is not None:
        lines += ["", "## Cross-family agreement", "| Dimension | Kappa |", "|---|---|"]
        lines += [f"| {dim} | {kappa:.2f} |" for dim, kappa in cross.kappa_by_dimension.items()]

    return "\n".join(lines)
