"""Agreement between two judge backends from different model families."""

from __future__ import annotations

from dataclasses import dataclass

from calibrate import cohen_kappa
from judge import JudgeBackend
from rubric import DIMENSIONS


@dataclass
class CrossCheckReport:
    kappa_by_dimension: dict[str, float]


def cross_check(primary: JudgeBackend, secondary: JudgeBackend, dataset: list[dict]) -> CrossCheckReport:
    primary_scores: dict[str, list[int]] = {dim: [] for dim in DIMENSIONS}
    secondary_scores: dict[str, list[int]] = {dim: [] for dim in DIMENSIONS}

    for item in dataset:
        primary_verdict = primary.score(item["question"], item["reference_answer"], item["candidate_answer"])
        secondary_verdict = secondary.score(item["question"], item["reference_answer"], item["candidate_answer"])
        for dim in DIMENSIONS:
            primary_scores[dim].append(getattr(primary_verdict, dim))
            secondary_scores[dim].append(getattr(secondary_verdict, dim))

    kappa_by_dimension = {
        dim: cohen_kappa(primary_scores[dim], secondary_scores[dim]) for dim in DIMENSIONS
    }
    return CrossCheckReport(kappa_by_dimension=kappa_by_dimension)
