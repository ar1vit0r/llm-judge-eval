"""Calibration: how trustworthy the judge is, not just what it says."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from judge import JudgeBackend
from rubric import DIMENSIONS


def cohen_kappa(labels_a: list[int], labels_b: list[int]) -> float:
    """Unweighted Cohen's kappa for two equal-length lists of discrete ratings.

    ponytail: hand-rolled instead of adding scikit-learn for one formula.
    """
    if len(labels_a) != len(labels_b):
        raise ValueError("label lists must be the same length")
    n = len(labels_a)
    if n == 0:
        raise ValueError("need at least one labeled pair")

    agreements = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    po = agreements / n

    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    categories = set(counts_a) | set(counts_b)
    pe = sum((counts_a.get(c, 0) / n) * (counts_b.get(c, 0) / n) for c in categories)

    if pe == 1.0:
        return 1.0  # only one category exists in both lists, no disagreement possible
    return (po - pe) / (1 - pe)


@dataclass
class CalibrationReport:
    kappa_by_dimension: dict[str, float]
    position_bias: float
    verbosity_bias: float


def position_bias(judge: JudgeBackend, question: str, reference: str, candidate: str) -> float:
    """Score delta when reference/candidate roles are swapped (should be ~0)."""
    forward = judge.score(question, reference, candidate)
    swapped = judge.score(question, candidate, reference)
    return abs(forward.overall - swapped.overall)


def verbosity_bias(judge: JudgeBackend, question: str, reference: str, candidate: str) -> float:
    """Score delta from padding the candidate with irrelevant filler (should be ~0)."""
    filler = "As previously mentioned, to elaborate further on this point, " * 3
    padded = f"{candidate} {filler}"
    base = judge.score(question, reference, candidate)
    inflated = judge.score(question, reference, padded)
    return inflated.overall - base.overall


def calibrate(judge: JudgeBackend, dataset: list[dict]) -> CalibrationReport:
    judge_scores: dict[str, list[int]] = {dim: [] for dim in DIMENSIONS}
    human_scores: dict[str, list[int]] = {dim: [] for dim in DIMENSIONS}

    for item in dataset:
        verdict = judge.score(item["question"], item["reference_answer"], item["candidate_answer"])
        for dim in DIMENSIONS:
            judge_scores[dim].append(getattr(verdict, dim))
            human_scores[dim].append(item["human_scores"][dim])

    kappa_by_dimension = {dim: cohen_kappa(judge_scores[dim], human_scores[dim]) for dim in DIMENSIONS}

    sample = dataset[0]
    pos_bias = position_bias(judge, sample["question"], sample["reference_answer"], sample["candidate_answer"])
    verb_bias = verbosity_bias(judge, sample["question"], sample["reference_answer"], sample["candidate_answer"])

    return CalibrationReport(
        kappa_by_dimension=kappa_by_dimension,
        position_bias=pos_bias,
        verbosity_bias=verb_bias,
    )
