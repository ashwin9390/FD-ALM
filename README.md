# FD-ALM: Framework-Driven Agent Lifecycle Management

Canonical naming:
- Project name: FD-ALM
- Python package: `fd_alm`
- CLI command: `fd-alm`

A governance layer for AI code agents, MCP servers and skills. It applies management frameworks (Cynefin, MoSCoW, RACI, Eisenhower, Pareto, Theory of Constraints, Wardley) as concrete controls: a registry of live entries, CI gatekeeper policies, triage rules for review routing, and AI-era cycle-time metrics.

> **Status: research concept with a starter implementation (v0.2).** No production deployment and no pilot data yet. Feedback and pilots welcome.

## Governance controls

FD-ALM enforces the following checks on live entries. The v0.2 milestone adds the provenance and lifecycle controls needed for accountable, reviewable governance over AI-era entries.

- **P1 / P1b**: owner accountability and CODEOWNERS alignment — every live entry must have an owner, and the owner must match the repository's CODEOWNERS rule for the entry's path.
- **P2**: human approval for high risk — complex or chaotic entries require explicit human approval before going live.
- **P3**: wildcards require justification — broad permissions (containing `*`) must be accompanied by written justification.
- **P4**: no `wont` items live — entries marked as `wont` in MoSCoW priority cannot be in live state.
- **P5**: stale entry detection — active entries unused for more than 90 days are flagged for deprecation review.
- **P6**: creator requirement — every live entry must record its creator so that provenance and accountability are preserved for AI-era systems.
- **P7**: kill criteria — every live entry must define exit conditions and metrics for deprecation, making lifecycle closure explicit and measurable.
- **P8**: kill review discipline — overdue kill reviews trigger a warning within a grace period and an error thereafter, enforcing regular lifecycle reviews and timely cleanup.

These controls provide the governance baseline for versioned entries, from ownership and approval through provenance, retirement, and operational review.
