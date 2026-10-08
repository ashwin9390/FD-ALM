# FD-ALM: Framework-Driven Agent Lifecycle Management

A governance layer for AI code agents, MCP servers and skills. It applies management frameworks (Cynefin, MoSCoW, RACI, Eisenhower, Pareto, Theory of Constraints, Wardley) as concrete controls: a governance model for ownership, risk, review, and lifecycle decisions.

> Status: research concept with a starter implementation (v0.1). No production deployment and no pilot data yet. Feedback and pilots welcome.

## Why

Teams add agents, MCP servers and skills faster than anyone can track them. Production gets cheap, human review becomes the bottleneck, and nobody can say who owns what. Read the full idea in [docs/spec.md](docs/spec.md) and the policy rules in [docs/policies.md](docs/policies.md).

## Quick start

```bash
pip install -e ".[dev]"

# 1. Gatekeeper: check the registry against policies (P1–P8) and CODEOWNERS
fd-alm check examples/registry.yaml --codeowners examples/CODEOWNERS --max-idle-days 90 --kill-grace-days 30

# 2. Review triage: order agent-authored changes for human review
fd-alm triage examples/registry.yaml examples/changes.yaml

# 3. Metrics: AI-era cycle time (AI processing + queue + human review)
fd-alm metrics examples/cycle_samples.csv

pytest
```

`check` exits with code 1 when a policy error is found, so it can gate a pull request in CI.

## How the frameworks become controls

| Framework | Where it lives in the code |
| --- | --- |
| **Cynefin** | `risk` field; `P2-human-approval` policy |
| **MoSCoW** | `priority` field; `P4-priority` policy |
| **RACI** | `owner` field; CODEOWNERS check (`P1`, `P1b`) |
| **Lifecycle & Provenance** | `last_used` (`P5-stale`), `creator` (`P6`), `kill_criterion` (`P7`, `P8`) policies |
| **Eisenhower** | Review triage quadrants (`triage.py`) |
| **Theory of Constraints** | Triage orders the queue around human review; metrics evaluate constraints (`metrics.py`) |
| **Pareto** | Planned: report which few agents drive most output or review burden |
| **Wardley** | Planned: build, buy or retire guidance per skill and MCP server |

## Repository layout

```text
.
├── README.md
├── LICENSE              Apache-2.0 (code)
├── LICENSE-docs         CC BY 4.0 (documentation and specification)
├── NOTICE
├── pyproject.toml
├── docs/
│   ├── spec.md          The FD-ALM specification
│   └── policies.md      Gatekeeper rules, fields, triage and CI usage
├── schema/
│   └── registry.schema.json
├── examples/
│   ├── registry.yaml
│   ├── CODEOWNERS
│   ├── changes.yaml
│   └── cycle_samples.csv
├── src/fd_alm/
│   ├── __init__.py      Package version
│   ├── registry.py      Registry model and YAML validation
│   ├── codeowners.py    Minimal CODEOWNERS parser (RACI owners)
│   ├── gatekeeper.py    Policy checks (P1–P8)
│   ├── triage.py        Review triage (Eisenhower)
│   ├── metrics.py       Cycle time and process efficiency
│   └── cli.py           fd-alm check | triage | metrics
├── tests/
│   └── test_fd_alm.py
└── .github/workflows/ci.yml
```

## Roadmap

* [x] Registry schema and example policies
* [x] Reference implementation: registry, gatekeeper, triage, metrics, CLI
* [ ] Pilot on a real repository with before-and-after cycle-time data
* [ ] Threat model for MCP and tool misuse
* [ ] Pareto and Wardley reports
* [ ] Optional runtime enforcement for teams that also want a gateway

## Feedback

If you run agents, MCP servers or skills at scale, which control would you try first, and what would make you reject it? Open an issue.

## License

| Part | License |
| --- | --- |
| Source code (`src/`, `tests/`, `examples/`, `.github/`) | [Apache License 2.0](./LICENSE) |
| Documentation and specification (`README.md`, `docs/`) | [Creative Commons Attribution 4.0 International](./LICENSE-docs) |

Copyright © 2026 Ashwin H. See [NOTICE](./NOTICE).
