# Gatekeeper policies

The gatekeeper is a set of plain, readable rules. Each one maps to a management framework from the [spec](spec.md). Errors fail the check (exit code 1); warnings are advice.

| Rule | Framework | Severity | What it checks |
|---|---|---|---|
| P1-owner-required | RACI | error | A live entry (`approved` or `active`) has an owner. No owner, no admission. |
| P1b-codeowners | RACI | error / warning | The registry owner matches the repository's CODEOWNERS for the entry's `path`. Error on mismatch, warning if no rule covers the path. |
| P2-human-approval | Cynefin | error | A live entry with `risk: complex` or `chaotic` has a named `approved_by`. |
| P3-broad-permissions | (least privilege) | error | A live entry with wildcard permissions (for example `tickets:*`) has a written `justification`. |
| P4-priority | MoSCoW | error | A `wont` entry is not live. |
| P5-stale | Lifecycle | warning | An `active` entry unused for more than `--max-idle-days` (default 90) is a candidate for deprecation. |

## Registry fields

| Field | Values | Meaning |
|---|---|---|
| `id`, `kind`, `name` | `kind`: agent, skill, mcp_server | Required identity |
| `owner` | team or handle | RACI accountable owner |
| `path` | repo path | Where the config lives; used to look up CODEOWNERS |
| `risk` | clear, complicated, complex, chaotic | Cynefin domain: how predictable the task is |
| `priority` | must, should, could, wont | MoSCoW admission priority |
| `state` | proposed, approved, active, deprecated, retired | Lifecycle state |
| `permissions` | list | What the entry can do |
| `justification`, `approved_by` | text | Evidence for broad permissions and high-risk approval |
| `last_used` | YYYY-MM-DD | Usage signal for retirement |

## Review triage

`fd-alm triage` orders agent-authored changes using Eisenhower quadrants. A change is **important** when its agent has `risk: complex` or `chaotic`, or is not in the registry. It is **urgent** when flagged `urgent: true`.

| Quadrant | Important | Urgent | Lane |
|---|---|---|---|
| Q1 | yes | yes | review now |
| Q2 | yes | no | schedule review |
| Q3 | no | yes | fast lane |
| Q4 | no | no | batch review |

Within a quadrant, smaller changes go first, because review time is the constraint.

## Metrics

`cycle time = AI processing + queue + human review`. `efficiency = (AI processing + review) / cycle time`, treating queue time as waiting. Change `VALUE_ADDING` in `src/fd_alm/metrics.py` if your team defines value-adding time differently. Compare before and after introducing an agent: if AI time drops but queue and review grow, throughput has not improved.

## Run it in CI (GitHub Actions)

```yaml
name: fd-alm
on: [pull_request]
jobs:
  governance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install git+https://github.com/ashwin9390/FD-ALM
      - run: fd-alm check registry.yaml --codeowners .github/CODEOWNERS
```
