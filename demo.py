"""Runnable self-check: runs the full pipeline on the sample dataset with the
zero-dependency HeuristicJudge (no API key needed) and asserts it doesn't blow up.

Note: the heuristic backend is a string-similarity stand-in, not a real judge,
so its kappa numbers are expected to be mediocre. Swap in LLMJudge (judge.py)
for calibration numbers that mean something.
"""

from __future__ import annotations

import json
from pathlib import Path

from calibrate import calibrate
from judge import HeuristicJudge
from report import build_report

DATASET_PATH = Path(__file__).parent / "dataset" / "qa_pairs.json"


def demo() -> None:
    dataset = json.loads(DATASET_PATH.read_text())
    judge = HeuristicJudge()
    calibration = calibrate(judge, dataset)

    assert set(calibration.kappa_by_dimension) == {"correctness", "completeness", "clarity", "safety"}
    for kappa in calibration.kappa_by_dimension.values():
        assert -1.0 <= kappa <= 1.0

    print(build_report(calibration))


if __name__ == "__main__":
    demo()
