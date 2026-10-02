# Agent Eval Lab technical overview

## Pipeline architecture

The system is an artifact-driven pipeline:

```text
config → plan → run → checks → judge → aggregate → compare → decide → report
```

Agent execution is the only expensive and nondeterministic stage. Every later stage reads persisted artifacts, so `report` and `judge` can be rerun without agent state in memory.

## Core data model

Pydantic models define the boundaries between stages. A `RunRecord` stores the task, arm, repetition, harness identity, model, adapter, duration, usage provenance, patch, and execution status. Checks, judge results, comparisons, decisions, and reports are serialized separately.

The artifact tree is the source of truth. SQLite is only a rebuildable index; deleting it does not delete evaluation evidence.

## Workspace isolation

Each run starts from a fixture copied into a temporary Git repository. The harness is overlaid before the agent starts and excluded from the Git diff. Protected paths are restored before verification, preventing an agent from weakening existing tests or configuration. Hidden verification files are copied in only after the agent stops.

`doctor` validates every benchmark before an evaluation. It rejects vacuous tasks, where the pristine fixture already passes, and unsolvable tasks, where the reference solution cannot pass.

## Metrics and statistical design

The system keeps objective and judged signals separate. Correctness is measured from checks; requirement adherence is judged from the prompt, rubric, diff, and relevant source context; quality is reported from lint/type checks and judge criteria; efficiency uses duration and usage provenance; reliability measures agreement across repetitions.

Repetitions are aggregated per task before comparison. This avoids pretending that three attempts on the same task are three independent tasks. Paired task differences and cluster bootstrap intervals express uncertainty without relying on a small-sample normal approximation.

## Decision logic

The verdict uses ordered gates rather than a weighted composite score:

1. Verify that the arms are comparable.
2. Reject a candidate with a critical task regression.
3. Flag tampering, judge disagreement, and measured-versus-judged conflicts for manual review.
4. Test whether the primary correctness interval clears the configured materiality threshold.
5. Apply cost, duration, quality, and reliability guardrails.

Each threshold is recorded in the configuration and included in the report. A verdict includes reasons naming the gates that fired.

## Judge isolation

The judge receives the task prompt, rubric, patch, and relevant repository context. It does not receive the harness identity, the other arm’s patch, or test/lint/type results. Evidence must cite a file and line; unsupported criteria are discarded instead of being treated as confident scores.

The offline heuristic provider is explicitly labelled as not being an LLM. A network provider is optional and should only be enabled after reviewing privacy and credential requirements.

## Reproducibility and safety

Artifacts are redacted before they are written. Missing adapter usage is represented as `unavailable`, while simulated usage is represented as `simulated`. The agent always works in a temporary copy, never in the user’s real repository. The test suite runs offline with mock providers and scripted runners.

