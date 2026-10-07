# FD-ALM: Framework-Driven Agent Lifecycle Management

**Author:** Ashwin H · **Version:** 0.1 · **Status:** research concept with a starter reference implementation (see the repository root). No production deployment and no pilot data yet. Designs below are proposals to be tested.

---

## 1. Summary

AI code agents, MCP servers and reusable "skills" are multiplying faster than organizations can track them. Teams gain speed, but nobody can say which agents exist, who owns them, what they can touch, or whether they are still used.

**FD-ALM is a governance layer that applies familiar management frameworks (Cynefin, MoSCoW, RACI, Eisenhower, Pareto, Theory of Constraints, Wardley) to the lifecycle of AI agents, MCP servers and skills.** Each agent becomes a managed asset with an owner, a risk class and a retirement date, instead of a free-floating script.

## 2. The problem

- **Sprawl.** Agents, MCP servers and skills are created per team, per project, per person. Many overlap. Few are retired.
- **Unclear ownership.** When an agent changes code or calls a tool, there is often no accountable human.
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
| **RACI** | Who is accountable? | Every agent, skill and MCP server has a named Responsible and Accountable owner |
| **Eisenhower** | How urgent and important is this change? | Routing rules for review triage |
| **Pareto** | Where does the value or the pain concentrate? | Find the few agents that produce most output, or most review burden |
| **Theory of Constraints** | What limits throughput? | Treat human review as the constraint and optimize around it |
| **Wardley** | How mature is this capability? | Build, buy, standardize or retire decisions for skills and MCP servers |

## 5. Architecture

Three components work together.

**Registry.** The inventory of every agent, skill and MCP server: purpose, owner (RACI), permissions, risk class (Cynefin), priority (MoSCoW) and lifecycle state.

**Gatekeeper.** Checks at the points where changes already pass: before an agent or tool is admitted, and before an agent-authored change merges. Example policies: no owner, no admission; a high-risk class requires human approval; broad permissions require justification.

**Review triage.** Routes agent-authored changes to human reviewers by risk and urgency (Eisenhower), so the scarce resource goes to the changes that need it (Theory of Constraints).

**Lifecycle states:** proposed → approved → active → deprecated → retired. Usage data drives the move to deprecated and retired, so the registry shrinks as well as grows.

## 6. Embedded variant (CI-native)

A central gateway that every agent call passes through is one way to enforce these controls. The alternative is to **embed** them in tooling engineering teams already use:

- **CI** acts as the gatekeeper, running policy checks in existing pipelines.
- **CODEOWNERS** supplies the accountable owner for each agent, skill or tool.
- **Dead-code tooling** identifies unused agents and skills for retirement.

Why embedded: no new single point of failure, no new queue, lower adoption friction, and the controls live next to the code they govern. The trade-off is weaker runtime enforcement than a gateway, so the two approaches can be combined.

## 7. Measuring efficiency

AI-era cycle time is redefined as:

> **Cycle time = AI processing time + queue time + human review time**

A process-efficiency metric sits on top of it. The standard form is **value-adding time ÷ total cycle time**.

How to use it: measure before and after introducing an agent. If AI processing shrinks but queue and review time grow, throughput has not improved, and the constraint is review. That is the Theory of Constraints argument in numbers.

## 8. Risks and limits

- **Governance theater.** A registry nobody updates is worse than none. Populate it automatically from CI and repositories.
- **Frameworks are sense-making, not enforcement.** Each needs a concrete threshold (for example, which Cynefin domain triggers which approval) before it is a control.
- **Process overhead.** Keep checks in existing tooling, and measure whether review time actually falls.
- **No evidence yet.** FD-ALM is a concept. Its claims need data from a real pilot.

## 9. Roadmap

1. ~~Publish a registry schema and example policies.~~ Done in v0.1: `schema/registry.schema.json`, `docs/policies.md`.
2. ~~Build a small reference implementation.~~ Started in v0.1: `src/fd_alm` (registry, CODEOWNERS support, gatekeeper, review triage, cycle-time metrics, CLI).
3. Run it on a real repository and report cycle time before and after.
4. Add a threat model for MCP and tool misuse (prompt injection, tool poisoning, over-broad permissions).
5. Add runtime enforcement options for teams that also want a gateway.

## 10. Feedback wanted

If you run agents, MCP servers or skills at scale, which control would you try first, and what would make you reject it? Open an issue or send a message.
