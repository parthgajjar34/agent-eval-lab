# Agent Eval Lab from a user’s perspective

## What problem does it solve?

Engineering teams frequently change the instructions and configuration around coding agents. They add skills, modify `AGENTS.md`, change permissions, connect tools, or switch models because they expect better results. The difficult question is whether the change actually helped.

Agent Eval Lab turns that question into a repeatable comparison. It runs the same software tasks with a baseline harness and a candidate harness, records the evidence, and explains whether the candidate produced a meaningful improvement.

## What does a user provide?

The user provides two harnesses:

- **Baseline:** the current agent setup.
- **Candidate:** the proposed setup being evaluated.

The user also provides a benchmark. A benchmark contains a starting codebase, task instructions, hidden verification tests, quality checks, and known-good reference solutions.

The hidden tests matter because the agent must solve the task from the prompt and repository, rather than simply reading the grader.

## What happens during an evaluation?

The tool creates an isolated temporary workspace for every attempt. It overlays one harness, lets the configured agent work, captures the patch, restores protected files, and runs the objective checks. It repeats this for both harnesses and for every task.

The optional judge reviews the patch against the task rubric. It does not receive test results, so test outcomes and subjective review remain separate signals.

## What does the user receive?

The result is a self-contained HTML report and a JSON report. The report shows:

- functional correctness;
- requirement adherence;
- lint and type-check quality;
- duration, tokens, and cost when available;
- reliability across repetitions;
- uncertainty intervals;
- manual-review findings;
- the exact reasons behind the verdict.

The verdict can be **POSITIVE**, **NEGATIVE**, **INCONCLUSIVE**, or **NOT_COMPARABLE**. `INCONCLUSIVE` is useful: it means the experiment did not collect enough evidence to justify a confident decision.

## How should a user run it?

For a quick presentation:

```powershell
agent-eval evaluate -c examples/live-demo.yaml
agent-eval report -c examples/live-demo.yaml
```

For a stronger offline comparison:

```powershell
agent-eval evaluate -c examples/demo.yaml
agent-eval report -c examples/demo.yaml
```

The offline demo uses real temporary workspaces and real checks. The agent attempts and usage values are simulated and labelled as such. A production evaluation can use `examples/real.yaml` with an installed agent and the organisation’s approved credentials.

## Why should a team trust the result?

Every stage leaves evidence on disk: prompts, patches, logs, checks, judge results, and report data. A reviewer can move from a report cell back to the artifact that produced it. Reports can also be rebuilt later without rerunning agents, which makes threshold changes and audits inexpensive and reproducible.

