"""Registry: the inventory of agents, skills and MCP servers.

Each entry carries the controls the framework mapping needs:
  risk      -> Cynefin domain (how predictable the task is)
  priority  -> MoSCoW (admission priority)
  owner     -> RACI (accountable owner)
  state     -> lifecycle (proposed -> approved -> active -> deprecated -> retired)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

KINDS = {"agent", "skill", "mcp_server"}
RISKS = ("clear", "complicated", "complex", "chaotic")  # Cynefin domains
PRIORITIES = ("must", "should", "could", "wont")  # MoSCoW
STATES = ("proposed", "approved", "active", "deprecated", "retired")

KILL_CRITERION_FIELDS = {"metric", "threshold", "comparator", "window", "action", "review_by"}
VALID_COMPARATORS = {"<", ">", "<=", ">="}
VALID_ACTIONS = {"deprecate", "retire", "notify"}


class RegistryError(ValueError):
    """Raised when a registry file is malformed."""


@dataclass
class Entry:
    id: str
    kind: str
    name: str
    owner: str = ""
    creator: str = ""
    path: str = ""  # where the agent/skill/tool config lives in the repo
    purpose: str = ""
    risk: str = "complicated"
    priority: str = "could"
    state: str = "proposed"
    permissions: list[str] = field(default_factory=list)
    justification: str = ""
    approved_by: str = ""
    last_used: date | None = None
    kill_criterion: dict[str, Any] | None = None


def _as_date(value: Any, entry_id: str) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise RegistryError(f"{entry_id}: last_used must be YYYY-MM-DD, got {value!r}") from exc


def _validate_kill_criterion(raw: Any, entry_id: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise RegistryError(f"{entry_id}: kill_criterion must be a mapping")

    missing = KILL_CRITERION_FIELDS - set(raw.keys())
    if missing:
        raise RegistryError(f"{entry_id}: kill_criterion is missing required fields: {sorted(missing)}")

    comparator = raw.get("comparator")
    if comparator not in VALID_COMPARATORS:
        raise RegistryError(f"{entry_id}: invalid kill_criterion comparator {comparator!r}")

    action = raw.get("action")
    if action not in VALID_ACTIONS:
        raise RegistryError(f"{entry_id}: invalid kill_criterion action {action!r}")

    return dict(raw)


def _parse_entry(raw: dict) -> Entry:
    if not isinstance(raw, dict):
        raise RegistryError(f"entry must be a mapping, got {type(raw).__name__}")
    for required in ("id", "kind", "name"):
        if not raw.get(required):
            raise RegistryError(f"entry is missing required field {required!r}: {raw}")
    eid = str(raw["id"])
    if raw["kind"] not in KINDS:
        raise RegistryError(f"{eid}: kind must be one of {sorted(KINDS)}, got {raw['kind']!r}")
    risk = raw.get("risk", "complicated")
    if risk not in RISKS:
        raise RegistryError(f"{eid}: risk must be one of {list(RISKS)}, got {risk!r}")
    priority = raw.get("priority", "could")
    if priority not in PRIORITIES:
        raise RegistryError(f"{eid}: priority must be one of {list(PRIORITIES)}, got {priority!r}")
    state = raw.get("state", "proposed")
    if state not in STATES:
        raise RegistryError(f"{eid}: state must be one of {list(STATES)}, got {state!r}")
    permissions = raw.get("permissions") or []
    if not isinstance(permissions, list):
        raise RegistryError(f"{eid}: permissions must be a list")

    kill_criterion = _validate_kill_criterion(raw.get("kill_criterion"), eid)

    return Entry(
        id=eid,
        kind=raw["kind"],
        name=str(raw["name"]),
        owner=str(raw.get("owner") or ""),
        creator=str(raw.get("creator") or ""),
        path=str(raw.get("path") or ""),
        purpose=str(raw.get("purpose") or ""),
        risk=risk,
        priority=priority,
        state=state,
        permissions=[str(p) for p in permissions],
        justification=str(raw.get("justification") or ""),
        approved_by=str(raw.get("approved_by") or ""),
        last_used=_as_date(raw.get("last_used"), eid),
        kill_criterion=kill_criterion,
    )


def parse_registry(data: dict) -> list[Entry]:
    """Parse already-loaded registry data (a mapping with an 'entries' list)."""
    if not isinstance(data, dict) or "entries" not in data:
        raise RegistryError("registry must be a mapping with an 'entries' list")
    entries = [_parse_entry(raw) for raw in data["entries"] or []]
    seen: set[str] = set()
    for entry in entries:
        if entry.id in seen:
            raise RegistryError(f"duplicate entry id: {entry.id}")
        seen.add(entry.id)
    return entries


def load_registry(path: str | Path) -> list[Entry]:
    with open(path, encoding="utf-8") as handle:
        return parse_registry(yaml.safe_load(handle))