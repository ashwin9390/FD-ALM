# FD-ALM: Framework-Driven Agent Lifecycle Management

**Author:** Ashwin H · **Version:** 0.2 (draft) · **Status:** research concept with a starter reference implementation (see the repository root). No production deployment and no pilot data yet. Designs below are proposals to be tested.

**What changed in 0.2:** ownership now follows the production outcome, not the authorship, so the registry records a `creator` and an accountable `owner` separately. Every live entry also carries a **kill criterion**, not just a lifecycle state. Both changes respond to public feedback on v0.1.

---

## 1. Summary

AI code agents, MCP servers and reusable "skills" are multiplying faster than organizations can track them. Teams gain speed, but nobody can say which agents exist, who answers for them, what they can touch, or when they should be switched off.

**FD-ALM is a governance layer that applies familiar management frameworks (Cynefin, MoSCoW, RACI, Eisenhower, Pareto, Theory of Constraints, Wardley) to the lifecycle of AI agents, MCP servers and skills.** Each agent becomes a managed asset with an accountable owner, a recorded creator, a risk class and a kill criterion, instead of a free-floating script.

## 2. The problem

- **Sprawl.** Agents, MCP servers and skills are created per team, per project, per person. Many overlap. Few are retired.
- **Unclear ownership.** When an agent changes code or calls a tool, there is often no accountable human. The person who built it is not necessarily the one who answers for what it does in production.
- **No exit.** Agents have a lifecycle state, but rarely a defined condition under which they get switched off.
- **The bottleneck moves.** AI makes producing a change cheap. Human review becomes the slowest step, so more AI output can lower overall throughput.
- **Security surface.** Every agent and tool connection is a permission boundary. Untracked ones are unreviewed attack surface.
- **Wrong metrics.** Classic cycle time ignores AI processing time and the queue that builds before review.

## 3. Core idea

Management frameworks already exist for deciding what to do, who decides, and where effort is wasted. FD-ALM uses them as **operating controls** for agents, so governance feels familiar to engineering and product leaders and needs no new vocabulary.

## 4. Framework mapping

| Framework | Question it answers for agents | Control it becomes |
|---|---|---|
| **Cynefin** | How predictable is this task? | Sets autonomy level: clear tasks run automatically, complex or chaotic ones need a human in the loop |
| **MoSCoW** | Which agents and skills matter? | Admission priority for the registry (must / should / could / won't) |
| **RACI** | Who answers for the output in production? | The `owner` is the accountable team, resolved in CODEOWNERS. The `creator` is recorded separately as provenance |
| **Eisenhower** | How urgent and important is this change? | Routing rules for review triage |
| **Pareto** | Where does the value or the pain concentrate? | Find the few agents that produce most output, or most review burden |
| **Theory of Constraints** | What limits throughput? | Treat human review as the constraint and optimize around it. Kill criteria can use the same metrics |
| **Wardley** | How mature is this capability? | Build, buy, standardize or retire decisions for skills and MCP servers |

## 5. Architecture

Three components work together.

**Registry.** The inventory of every agent, skill and MCP server: purpose, creator, owner (RACI), permissions, risk class (Cynefin), priority (MoSCoW), lifecycle state and kill criterion.

**Gatekeeper.** Checks at the points where changes already pass: before an agent or tool is admitted, and before an agent-authored change merges. Example policies: no owner, no admission; a high-risk class requires human approval; broad permissions require justification; no kill criterion, no activation.

**Review triage.** Routes agent-authored changes to human reviewers by risk and urgency (Eisenhower), so the scarce resource goes to the changes that need it (Theory of Constraints).

**Lifecycle states:** proposed → approved → active → deprecated → retired. Usage data and kill criteria drive the move to deprecated and retired, so the registry shrinks as well as grows.

### 5.1 Ownership follows the outcome, not the authorship

Two roles are kept apart:

- **Creator:** whoever built or configured the entry. Recorded for provenance. Carries no accountability by default.
- **Owner:** whoever answers for its output in production. They take the incident, explain the behavior and decide whether to keep it. The owner must resolve in CODEOWNERS for the entry's path.

Rules:

1. A live entry (anything past `proposed`) must have an owner.
2. The owner must match a CODEOWNERS entry covering the entry's path.
3. Creator and owner may be the same. They are separate fields so that a person changing teams never silently moves accountability.
4. When an owner changes, the registry entry changes in a pull request. That is the audit trail.
5. Migration from 0.1: copy the old `owner` into `creator`, then have the accountable team confirm or replace `owner`.

### 5.2 Kill criteria

A kill criterion states, before the agent ships, what "not worth keeping" looks like, and forces a recurring look at it.

| Field | Meaning |
|---|---|
| `metric` | What is measured, for example `review_hours_per_change`, `ai_cycle_time_days`, `rejection_rate` |
| `threshold`, `comparator` | The line that triggers the action (`>`, `>=`, `<`, `<=`) |
| `window` | Consecutive periods the breach must persist (default 1) |
| `action` | `deprecate`, `retire` or `escalate` to a human decision |
| `review_by` | Date by which the owner must re-confirm or change the criterion |

An entry can stay in `proposed` without one. It cannot become `active` without one. The exact thresholds are judgment calls until a pilot supplies data; the requirement is that someone decided.

### 5.3 Example registry entry

```yaml
entries:
  - id: pr-summarizer
    kind: agent
    name: PR summarizer
    creator: "@ashwin9390"
    owner: "@platform/dev-experience"
    path: agents/pr-summarizer/
    risk: complicated
    priority: should
    state: active
    kill_criterion:
      metric: review_hours_per_change
      threshold: 0.5
      comparator: ">"
      window: 2
      action: deprecate
      review_by: 2027-01-31
```

## 6. Embedded variant (CI-native)

A central gateway that every agent call passes through is one way to enforce these controls. The alternative is to **embed** them in tooling engineering teams already use:

- **CI** acts as the gatekeeper, running policy checks in existing pipelines.
- **CODEOWNERS** supplies the accountable owner for each agent, skill or tool.
- **Dead-code tooling** identifies unused agents and skills for retirement.

Why embedded: no new single point of failure, no new queue, lower adoption friction, and the controls live next to the code they govern. The trade-off is weaker runtime enforcement than a gateway, so the two approaches can be combined.

## 7. Gatekeeper policies

| Policy | Severity | Rule |
|---|---|---|
| `P1-owner-required` | error | A live entry has an owner |
| `P1b-codeowners` | error | The owner matches a CODEOWNERS entry covering the path |
| `P2-human-approval` | error | High-risk classes (complex, chaotic) need `approved_by` |
| `P3-broad-permissions` | error | Wildcard permissions need a justification |
| `P4-priority` | error | A `wont` priority cannot be live |
| `P5-stale` | warning | An active entry has not been used within the idle window |
| `P6-creator-required` | error | A live entry records its creator |
| `P7-kill-criterion` | error | An `active` entry has a complete kill criterion |
| `P8-kill-review-overdue` | warning, then error | `review_by` has passed. Becomes an error after a configurable grace period (default 30 days) |

## 8. Measuring efficiency

AI-era cycle time is redefined as:

> **Cycle time = AI processing time + queue time + human review time**

A process-efficiency metric sits on top of it. The standard form is **value-adding time ÷ total cycle time**.

How to use it: measure before and after introducing an agent. If AI processing shrinks but queue and review time grow, throughput has not improved, and the constraint is review. That is the Theory of Constraints argument in numbers.

The same metrics can feed kill criteria. An agent whose changes add more review time than they save is a candidate for `deprecate`.

## 9. Risks and limits

- **Governance theater.** A registry nobody updates is worse than none. Populate it automatically from CI and repositories. A kill criterion nobody reviews is the same failure, which is why `review_by` is required.
- **Frameworks are sense-making, not enforcement.** Each needs a concrete threshold (for example, which Cynefin domain triggers which approval) before it is a control.
- **Thresholds are guesses until measured.** Kill-criterion values need pilot data.
- **Process overhead.** Keep checks in existing tooling, and measure whether review time actually falls.
- **No evidence yet.** FD-ALM is a concept. Its claims need data from a real pilot.

## 10. Roadmap

1. ~~Publish a registry schema and example policies.~~ Done in v0.1.
2. ~~Build a small reference implementation.~~ Started in v0.1: `src/fd_alm`.
3. Creator/owner split and kill criteria (v0.2, this draft).
4. Command that evaluates kill criteria against measured metrics and reports breaches.
5. Run it on a real repository and report cycle time before and after.
6. Add a threat model for MCP and tool misuse (prompt injection, tool poisoning, over-broad permissions).
7. Add runtime enforcement options for teams that also want a gateway.

Open question: should `owner` allow a primary and a secondary, or is a single accountable owner the stronger rule?

## 11. Feedback wanted

If you run agents, MCP servers or skills at scale, which control would you try first, and what would make you reject it? Open an issue or send a message.
