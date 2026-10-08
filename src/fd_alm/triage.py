"""AI-era cycle time and process efficiency.

    cycle time = AI processing time + queue time + human review time

Process efficiency = value-adding time / total cycle time. By default, AI processing and
human review count as value-adding (work is happening) and queue time does not (waiting).
Change `VALUE_ADDING` if your team defines it differently.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import median

VALUE_ADDING = ("ai_s", "review_s")


@dataclass(frozen=True)
class Sample:
    ai_s: float
    queue_s: float
    review_s: float

    @property
    def cycle_s(self) -> float:
        return self.ai_s + self.queue_s + self.review_s

    @property
    def efficiency(self) -> float:
        total = self.cycle_s
        if total == 0:
            return 0.0
        return sum(getattr(self, name) for name in VALUE_ADDING) / total


def load_samples(path: str | Path) -> list[Sample]:
    with open(path, newline="", encoding="utf-8") as handle:
        return [
            Sample(float(r["ai_s"]), float(r["queue_s"]), float(r["review_s"]))
            for r in csv.DictReader(handle)
        ]


def summarize(samples: list[Sample]) -> dict[str, float]:
    if not samples:
        raise ValueError("no samples")
    return {
        "n": len(samples),
        "median_cycle_s": median(s.cycle_s for s in samples),
        "median_ai_s": median(s.ai_s for s in samples),
        "median_queue_s": median(s.queue_s for s in samples),
        "median_review_s": median(s.review_s for s in samples),
        "median_efficiency": median(s.efficiency for s in samples),
    }


def compare(before: list[Sample], after: list[Sample]) -> dict[str, float]:
    """Relative change in medians (negative = faster). Review is the constraint to watch."""
    b, a = summarize(before), summarize(after)
    return {
        key: (a[key] - b[key]) / b[key] if b[key] else 0.0
        for key in ("median_cycle_s", "median_ai_s", "median_queue_s", "median_review_s")
    }
