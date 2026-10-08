# FD-ALM: Framework-Driven Agent Lifecycle Management

FD-ALM is a governance layer for AI code agents, MCP servers, and skills. It translates established management frameworks into practical controls for ownership, review, risk, and lifecycle policy.

The project applies Cynefin, MoSCoW, RACI, Eisenhower, Pareto, Theory of Constraints, and Wardley thinking as concrete operating rules for real-world agent ecosystems.

> Status: research concept with a starter implementation (v0.1). No production deployment or pilot data yet. Feedback and pilots are welcome.

## Why

Teams add agents, MCP servers, and skills faster than they can track them. As adoption grows, cheap production execution creates a human review bottleneck and the question of ownership becomes harder to answer.

FD-ALM aims to make those concerns visible and governable before they become operational risk. The underlying concept is described in [docs/spec.md](docs/spec.md), and the policy rules live in [docs/policies.md](docs/policies.md).

## Quick start

```bash
pip install -e ".[dev]"

# 1. Gatekeeper: check the registry against P1–P8 policies and CODEOWNERS
fd-alm check examples/registry.yaml --codeowners examples/CODEOWNERS --max-idle-days 90 --kill-grace-days 30

# 2. Review triage: prioritize agent-authored changes for human review
fd-alm triage examples/registry.yaml examples/changes.yaml

# 3. Metrics: measure AI-era cycle time (AI work + queue + human review)
fd-alm metrics examples/cycle_samples.csv

pytest
```

`check` exits with code 1 when a policy violation is found, so it can be used to gate a pull request in CI.

## How the frameworks become controls

| Framework | Where it lives in the code |
| --- | --- |
| **Cynefin** | `risk` field and `P2-human-approval` policy |
| **MoSCoW** | `priority` field and `P4-priority` policy |
| **RACI** | `owner` field and CODEOWNERS checks (`P1`, `P1b`) |
| **Lifecycle & Provenance** | `last_used` (`P5-stale`), `creator` (`P6`), and `kill_criterion` (`P7`, `P8`) policies |
| **Eisenhower** | Review triage quadrants in `triage.py` |
| **Theory of Constraints** | Triage ordering around human review capacity and metrics in `metrics.py` |
| **Pareto** | Planned: identify the few agents or skills that drive most output or review burden |
| **Wardley** | Planned: decide what to build, buy, or retire for skills and MCP servers |

## Repository layout

```text
.
├── README.md
├── LICENSE              Apache-2.0 (source code)
├── LICENSE-docs         CC BY 4.0 (documentation and specification)
├── NOTICE
├── pyproject.toml
├── docs/
│   ├── spec.md          FD-ALM specification
│   └── policies.md      Gatekeeper rules, fields, triage, and CI usage
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
│   ├── codeowners.py    Minimal CODEOWNERS parser for RACI ownership
│   ├── gatekeeper.py    Policy checks (P1–P8)
│   ├── triage.py        Review triage (Eisenhower)
│   ├── metrics.py       Cycle time and process efficiency
│   └── cli.py           fd-alm check | triage | metrics
├── tests/
│   └── test_fd_alm.py
├── .github/workflows/
│   └── ci.yml
└── .gitignore
```

## Roadmap

* [x] Registry schema and example policies
* [x] Reference implementation: registry, gatekeeper, triage, metrics, and CLI
* [ ] Pilot in a real repository with before-and-after cycle-time data
* [ ] Threat model for MCP and tool misuse
* [ ] Pareto and Wardley reports
* [ ] Optional runtime enforcement for teams that want gateway-style controls

## Feedback

If you run agents, MCP servers, or skills at scale, which control would you try first, and what would make you reject it? Open an issue.

## License

| Part | License |
| --- | --- |
| Source code (`src/`, `tests/`, `examples/`, `.github/`) | [Apache License 2.0](./LICENSE) |
| Documentation and specification (`README.md`, `docs/`) | [Creative Commons Attribution 4.0 International](./LICENSE-docs) |

Copyright © 2026 Ashwin H. See [NOTICE](./NOTICE).
