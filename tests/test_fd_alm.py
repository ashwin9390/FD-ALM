from datetime import date

import pytest

from fd_alm.codeowners import owners_for, parse_codeowners
from fd_alm.gatekeeper import check, has_errors
from fd_alm.metrics import Sample, compare, summarize
from fd_alm.registry import RegistryError, parse_registry
from fd_alm.triage import Change, triage

TODAY = date(2026, 10, 7)


def reg(*entries):
    return parse_registry({"entries": list(entries)})


def entry(**overrides):
    base = {"id": "a1", "kind": "agent", "name": "Agent", "owner": "@team", "state": "active"}
    base.update(overrides)
    return base


# registry -----------------------------------------------------------------------------------
def test_registry_rejects_bad_enum():
    with pytest.raises(RegistryError):
        reg(entry(risk="wild"))


def test_registry_rejects_duplicate_ids():
    with pytest.raises(RegistryError):
        reg(entry(), entry())


def test_registry_requires_fields():
    with pytest.raises(RegistryError):
        reg({"id": "x"})


# codeowners ---------------------------------------------------------------------------------
def test_codeowners_last_match_wins():
    rules = parse_codeowners("* @all\n/agents/ @agents\n/agents/refactor/ @backend  # note\n")
    assert owners_for("README.md", rules) == ["@all"]
    assert owners_for("agents/code-review/x.yaml", rules) == ["@agents"]
    assert owners_for("agents/refactor/x.yaml", rules) == ["@backend"]


def test_codeowners_no_match():
    assert owners_for("docs/a.md", parse_codeowners("/agents/ @a")) == []


# gatekeeper ---------------------------------------------------------------------------------
def rules_of(findings):
    return {f.rule for f in findings}


def test_live_entry_without_owner_is_an_error():
    findings = check(reg(entry(owner="")), today=TODAY)
    assert "P1-owner-required" in rules_of(findings) and has_errors(findings)


def test_proposed_entry_without_owner_is_allowed():
    assert check(reg(entry(owner="", state="proposed")), today=TODAY) == []


def test_codeowner_mismatch_is_an_error():
    rules = parse_codeowners("/agents/ @platform")
    findings = check(reg(entry(owner="@other", path="agents/a1/")), rules, today=TODAY)
    assert "P1b-codeowners" in rules_of(findings) and has_errors(findings)


def test_codeowner_match_passes():
    rules = parse_codeowners("/agents/ @team")
    assert check(reg(entry(path="agents/a1/")), rules, today=TODAY) == []


def test_high_risk_needs_human_approval():
    assert "P2-human-approval" in rules_of(check(reg(entry(risk="complex")), today=TODAY))
    assert check(reg(entry(risk="complex", approved_by="@lead")), today=TODAY) == []


def test_wildcard_permissions_need_justification():
    findings = check(reg(entry(permissions=["tickets:*"])), today=TODAY)
    assert "P3-broad-permissions" in rules_of(findings)
    assert check(reg(entry(permissions=["tickets:*"], justification="needed")), today=TODAY) == []


def test_wont_priority_cannot_be_live():
    assert "P4-priority" in rules_of(check(reg(entry(priority="wont")), today=TODAY))


def test_stale_active_entry_warns_but_does_not_fail():
    findings = check(reg(entry(last_used="2026-01-01")), today=TODAY, max_idle_days=90)
    assert "P5-stale" in rules_of(findings) and not has_errors(findings)


# triage -------------------------------------------------------------------------------------
def test_triage_orders_by_quadrant_then_size():
    entries = reg(entry(id="safe", risk="clear"), entry(id="risky", risk="complex", approved_by="@x"))
    changes = [
        Change("c-low", "low", "safe", urgent=False, lines_changed=5),
        Change("c-fast", "fast", "safe", urgent=True, lines_changed=2),
        Change("c-big", "big", "risky", urgent=True, lines_changed=800),
        Change("c-sched", "sched", "risky", urgent=False, lines_changed=100),
        Change("c-unknown", "unknown", "ghost", urgent=False, lines_changed=10),
    ]
    queue = triage(changes, entries)
    assert [t.change.id for t in queue] == ["c-big", "c-unknown", "c-sched", "c-fast", "c-low"]
    assert queue[0].quadrant == "Q1" and queue[-1].quadrant == "Q4"
    assert next(t for t in queue if t.change.id == "c-unknown").reason == "unregistered agent"


# metrics ------------------------------------------------------------------------------------
def test_cycle_time_and_efficiency():
    s = Sample(ai_s=60, queue_s=300, review_s=140)
    assert s.cycle_s == 500
    assert s.efficiency == pytest.approx(0.4)


def test_summarize_and_compare():
    before = [Sample(100, 100, 100)] * 3
    after = [Sample(10, 400, 100)] * 3
    assert summarize(after)["median_cycle_s"] == 510
    change = compare(before, after)
    assert change["median_ai_s"] == pytest.approx(-0.9)
    assert change["median_queue_s"] == pytest.approx(3.0)  # AI got faster, queue grew: review is the constraint
