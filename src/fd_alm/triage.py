"""Review triage: route agent-authored changes to human reviewers by risk and urgency.

Eisenhower quadrants:
  important = the authoring agent is high risk (complex/chaotic) or unregistered
  urgent    = the change is flagged urgent
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .registry import Entry

HIGH_RISK = {"complex", "chaotic"}

LANES = {
    (True, True): ("Q1", "review now"),
    (True, False): ("Q2", "schedule review"),
    (False, True): ("Q3", "fast lane"),
    (False, False): ("Q4", "batch review"),
}
ORDER = {"Q1": 0, "Q2": 1, "Q3": 2, "Q4": 3}


@dataclass(frozen=True)
class Change:
    id: str
    title: str
    agent: str
    urgent: bool = False
    lines_changed: int = 0


@dataclass(frozen=True)
class Triaged:
    change: Change
    quadrant: str
    lane: str
    reason: str


def load_changes(path: str | Path) -> list[Change]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return [
        Change(
            id=str(c["id"]),
            title=str(c.get("title", "")),
            agent=str(c["agent"]),
            urgent=bool(c.get("urgent", False)),
            lines_changed=int(c.get("lines_changed", 0)),
        )
        for c in data.get("changes", [])
    ]


def triage(changes: list[Change], entries: list[Entry]) -> list[Triaged]:
    by_id = {e.id: e for e in entries}
    result: list[Triaged] = []
    for c in changes:
        entry = by_id.get(c.agent)
        if entry is None:
            important, reason = True, "unregistered agent"
        else:
            important = entry.risk in HIGH_RISK
            reason = f"agent risk '{entry.risk}'"
        quadrant, lane = LANES[(important, c.urgent)]
        result.append(Triaged(c, quadrant, lane, reason))
    # Review is the constraint, so order the queue: most important and urgent first, small changes first.
    return sorted(result, key=lambda t: (ORDER[t.quadrant], t.change.lines_changed))
