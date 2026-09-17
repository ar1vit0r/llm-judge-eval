# llm-judge-eval

Rubric-based LLM-as-judge framework, calibrated against human labels. Scores LLM outputs on a fixed benchmark and reports how trustworthy the judge itself is, not just the scores it gives.

Scoped from [ar1vit0r/portfolio roadmap](https://github.com/ar1vit0r/portfolio/blob/main/roadmap/consolidated-roadmap.md), item #3 in the Python demo projects table.

## Why

A judge that just asks an LLM "rate this 1-5" doesn't prove much in 2026. This one locks a rubric, measures Cohen's kappa against human labels, checks for position/verbosity bias, and cross-checks against a second model family, the signals that separate a real eval harness from a toy.

## Scope

- Domain: reasoning/math QA pairs (e.g. a GSM8K subset), easiest to source a labeled benchmark and keeps rubric design tractable.
- Judge model: pluggable backend (cheap heuristic or real LLM), documented swap point for the cross-family check.
- Stack: Python, Pydantic for structured judge output, an LLM API client. No other new dependency.

## Architecture

| File | Purpose |
|------|---------|
| `dataset/` | 30-50 labeled QA pairs with human gold scores (correctness, completeness, clarity, safety, 1-5 each) |
| `rubric.py` | Locked rubric as a versioned prompt template + Pydantic schema for judge output |
| `judge.py` | Calls the judge model, returns structured scores; swappable backend |
| `calibrate.py` | Cohen's kappa between judge and human labels; position/verbosity bias checks |
| `cross_check.py` | Same rubric through a second, different-family model; reports agreement |
| `report.py` | Scorecard output: kappa, bias deltas, cross-family agreement |

## Deliverables

- Public repo, $0 deploy (runs locally).
- README with architecture diagram, sample judge output, the calibration scorecard as a table, and a "what this catches that a naive LLM-judge misses" section.
- One `demo()`/`__main__` self-check that runs the full pipeline on the sample dataset and asserts kappa computes without error.

## Not in scope (v1)

Fine-tuning a judge model, a UI/dashboard, production deployment, agent-as-judge.

## Status

Scoped, not started.
