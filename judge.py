"""Pluggable judge backends: a zero-dependency heuristic default and an LLM-backed judge."""

from __future__ import annotations

import difflib
import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

from rubric import RUBRIC_PROMPT, JudgeScore


class JudgeBackend(ABC):
    """Scores a candidate answer against a reference answer for a given question."""

    @abstractmethod
    def score(self, question: str, reference: str, candidate: str) -> JudgeScore: ...


class HeuristicJudge(JudgeBackend):
    """Deterministic, dependency-free judge for fast local runs (no API key needed).

    ponytail: string-similarity heuristic, not a real judge. It exists so `demo.py`
    runs offline; swap in LLMJudge for real calibration numbers.
    """

    def score(self, question: str, reference: str, candidate: str) -> JudgeScore:
        similarity = difflib.SequenceMatcher(None, reference.lower(), candidate.lower()).ratio()
        correctness = round(1 + similarity * 4)
        length_ratio = min(len(candidate) / max(len(reference), 1), 2.0)
        completeness = round(1 + min(length_ratio, 1.0) * 4)
        padding_penalty = max(0, length_ratio - 1.0)
        clarity = round(max(1, 5 - padding_penalty * 3))
        safety = 5
        return JudgeScore(
            correctness=correctness,
            completeness=completeness,
            clarity=clarity,
            safety=safety,
            rationale="heuristic: string similarity + length ratio",
        )


class LLMJudge(JudgeBackend):
    """Calls an LLM's chat API over stdlib HTTP (no SDK dependency)."""

    def __init__(
        self,
        model: str = "claude-haiku-4-5-20251001",
        api_key_env: str = "ANTHROPIC_API_KEY",
        api_url: str = "https://api.anthropic.com/v1/messages",
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.api_url = api_url

    def score(self, question: str, reference: str, candidate: str) -> JudgeScore:
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"{self.api_key_env} not set, cannot call LLMJudge")

        prompt = RUBRIC_PROMPT.format(question=question, reference=reference, candidate=candidate)
        payload = json.dumps(
            {
                "model": self.model,
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode()

        request = urllib.request.Request(
            self.api_url,
            data=payload,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read())
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLMJudge request failed: {exc}") from exc

        text = body["content"][0]["text"]
        return JudgeScore.model_validate_json(text)
