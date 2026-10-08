"""Gatekeeper: policy checks that run where changes already pass (CI)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .codeowners import Rule, owners_for
from .registry import Entry

ERROR = "error"
WARNING = "warning"
HIGH_RISK = {"complex", "chaotic"}
LIVE_STATES = {"approved", "active"}


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    entry_id: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.rule} {self.entry_id}: {self.message}"


def _is_broad(permission: str) -> bool:
    return "*" in permission


def check(
    entries: list[Entry],
    codeowners: list[Rule] | None = None,
    today: date | None = None,
    max_idle_days: int = 90,
    kill_grace_days: int = 30,
) -> list[Finding]:
    """Run all policies. Policies are plain, readable rules; see docs/policies.md."""
    today = today or date.today()
    findings: list[Finding] = []
    for e in entries:
        live = e.state in LIVE_STATES

        # P1 (RACI): no owner, no admission. A live entry needs an accountable owner.
        if live and not e.owner:
            findings.append(Finding("P1-owner-required", ERROR, e.id, "live entry has no owner"))

        # P1b: the owner must agree with the repository's CODEOWNERS for the entry's path.
        if codeowners is not None and e.path and e.owner:
            repo_owners = owners_for(e.path, codeowners)
            if not repo_owners:
                findings.append(Finding("P1b-codeowners", WARNING, e.id, f"no CODEOWNERS rule covers {e.path}"))
            elif e.owner not in repo_owners:
                findings.append(
                    Finding("P1b-codeowners", ERROR, e.id,
                            f"owner {e.owner} is not a CODEOWNER of {e.path} (found: {', '.join(repo_owners)})")
                )

        # P2 (Cynefin): complex/chaotic work needs a named human approver before it goes live.
        if live and e.risk in HIGH_RISK and not e.approved_by:
            findings.append(
                Finding("P2-human-approval", ERROR, e.id, f"risk '{e.risk}' requires approved_by before going live")
            )

        # P3: broad permissions need a written justification.
        broad = [p for p in e.permissions if _is_broad(p)]
        if live and broad and not e.justification:
            findings.append(
                Finding("P3-broad-permissions", ERROR, e.id,
                        f"wildcard permissions {broad} need a justification")
            )

        # P4 (MoSCoW): 'wont' items must not be live.
        if live and e.priority == "wont":
            findings.append(Finding("P4-priority", ERROR, e.id, "priority 'wont' but entry is live"))

        # P5 (lifecycle): active entries unused for a long time are candidates for deprecation.
        if e.state == "active" and e.last_used is not None:
            idle = (today - e.last_used).days
            if idle > max_idle_days:
                findings.append(
                    Finding("P5-stale", WARNING, e.id,
                            f"unused for {idle} days (limit {max_idle_days}); consider deprecating")
                )

        # P6: live entries must declare their creator for provenance tracking.
        if live and not e.creator:
            findings.append(Finding("P6-creator-required", ERROR, e.id, "live entry has no creator"))

        # P7: a live entry needs a declared kill criterion with concrete exit conditions.
        if live and e.kill_criterion is None:
            findings.append(Finding("P7-kill-criterion", ERROR, e.id, "live entry has no kill criterion"))

        # P8: kill reviews must happen on time; a grace period allows warnings before failures.
        if live and e.kill_criterion is not None:
            review_by = e.kill_criterion.get("review_by")
            if review_by is not None:
                try:
                    review_date = date.fromisoformat(str(review_by))
                except ValueError:
                    review_date = None
                if review_date is not None:
                    overdue_days = (today - review_date).days
                    if overdue_days > 0:
                        severity = WARNING if overdue_days <= kill_grace_days else ERROR
                        findings.append(
                            Finding(
                                "P8-kill-review-overdue",
                                severity,
                                e.id,
                                f"kill review was due on {review_date.isoformat()} ({overdue_days} day(s) overdue)",
                            )
                        )
    return findings


def has_errors(findings: list[Finding]) -> bool:
    return any(f.severity == ERROR for f in findings)
