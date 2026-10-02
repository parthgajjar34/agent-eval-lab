# Understanding and demonstrating Agent Eval Lab

## What to say first

“This tool evaluates whether changing a coding agent's instructions and settings
improves its results. It compares the current setup with a proposed setup on the
same coding tasks, repeats the experiment, and produces a report with the evidence
and uncertainty behind its conclusion.”

The product is a Python command-line application that generates a static HTML
report. The customer-records service inside `benchmarks/` is sample code used to
test agents; it is not the product being delivered.

## Vocabulary

| Term | Meaning |
|---|---|
| Agent | The coding tool that edits files, such as Claude Code |
| Model | The language model used by that agent |
| Harness | Instructions, skills, permissions, and configuration around the agent |
| Baseline | The current harness |
| Candidate | The proposed harness |
| Arm | One side of the comparison: baseline or candidate |
| Benchmark | A starting codebase plus a collection of coding tasks |
| Fixture | The starting codebase copied into each temporary workspace |
| Repetition | Another attempt at the same task under the same harness |
| Artifact | A saved result, patch, log, or other evidence file |
| Judge | An optional rubric-based assessment of the patch |

## The included experiment

The baseline asks the agent to run tests and keep code tidy. The candidate adds
instructions to inspect nearby code, reuse helpers, follow error and validation
conventions, preserve existing callers, and run tests, lint, and type checks. It
also adds `.claude/skills/repo-conventions/SKILL.md`.

Both harness manifests declare the same model and agent settings. The experiment
therefore aims to evaluate the instruction changes.

The benchmark contains five tasks:

1. Add CSV export with the existing customer filters.
2. Make missing-customer lookup fail clearly.
3. Validate imported rows and add tests.
4. Add pagination without breaking existing callers.
5. Extract reusable filtering logic without changing behavior.

The demo runs five tasks under two harnesses, three times each: 30 runs.

## End-to-end workflow

1. Load YAML configuration and the benchmark and harness files.
2. Validate the benchmark with `doctor`: the untouched fixture must fail the task's
   correctness checks, pass its quality checks, and pass all checks after applying
   the reference solution.
3. Create a plan identifying each task, harness, repetition, and execution order.
4. Create a fresh temporary Git workspace and overlay the selected harness.
5. Run the agent adapter and capture its patch, logs, and reported usage.
6. Restore modifications or deletions to protected existing files, recording
   tampering. Legitimate newly added tests survive.
7. Inject hidden verification tests after the agent stops and run objective checks.
8. Optionally judge the patch against its task rubric, without exposing the arm or
   test results to the judge.
9. Aggregate repetitions within each task, then compare the paired task results.
10. Apply decision rules and generate JSON and HTML reports.

Artifacts preserve the evidence so the report can be rebuilt without another agent
run. Re-judging also avoids rerunning the coding agent, but a network judge can
still incur usage and produce different assessments. Keep the original benchmark,
harness files, and configuration available for rebuilding reports: the current
implementation loads these inputs too.

## How results should be explained

| Dimension | Question |
|---|---|
| Correctness | Did the task pass its objective verification checks? |
| Requirement adherence | Does the patch satisfy the written requirement and rubric? |
| Quality/conventions | Does it pass lint/type checks and follow repository conventions? |
| Efficiency | What duration, tokens, cost, and turns were reported? |
| Reliability | How consistently did repetitions produce the same pass/fail outcome? |

Reliability alone does not mean success: consistently failing is also consistent.
Measured checks and judged assessments stay separate. Missing usage is unavailable,
not zero; demo usage is explicitly simulated.

The system does not combine these dimensions into a weighted overall score. Its
ordered rules check comparability, critical regressions, review flags, correctness
changes, guardrails, and sample size.

Possible verdicts are POSITIVE, NEGATIVE, INCONCLUSIVE, and NOT_COMPARABLE. Manual
review is a separate flag. A critical task regression can veto an average gain.
INCONCLUSIVE means the evidence does not support an actionable conclusion.

The statistical unit is the task. Three attempts at each of five tasks still give
five task comparisons, not fifteen independent task comparisons. The report uses
paired bootstrap intervals to express uncertainty. The default correctness
materiality threshold is 20 percentage points; an observed improvement alone does
not establish that the threshold is met.

## Demo mode versus real mode

| Mode | What happens |
|---|---|
| Simulated | Applies prepared code changes, runs real checks, uses declared usage figures |
| Claude Code | Invokes the real coding agent in temporary workspaces |
| Replay | Applies previously recorded patches and runs checks using recorded usage |

`examples/demo.yaml` uses the simulated adapter and a rule-based heuristic judge.
It needs no API key. It does not measure how a live model responds to the harness.
Say this explicitly before presenting its numbers.

`examples/real.yaml` uses Claude Code for both execution and judging. It requires
the configured CLI and credentials. Repository content is processed by the selected
provider. The shared agent/judge model family is a potential source of assessment
bias. This example is configuration, not proof of a successful live evaluation.

## Suggested client demonstration: 8–10 minutes

1. **Purpose, 1 minute:** explain the rollout decision the tool supports.
2. **Harness comparison, 1 minute:** show the baseline and candidate `AGENTS.md`
   files and the candidate skill. Explain what changed and what stayed constant.
3. **Benchmark, 1 minute:** show a task prompt, its hidden verification tests, and
   reference solution. Explain why the agent does not see the hidden tests.
4. **Execution, 1–2 minutes:** show `examples/live-demo.yaml` and run the offline
   evaluation. This configuration performs one repetition of every task (10 runs).
   Prepare a completed report beforehand so the presentation does not depend on
   execution speed. Printed simulated durations are not actual demo elapsed times.
5. **Report, 3 minutes:** start with the verdict and reasons, then harness changes,
   measured versus judged metrics, per-task results, and manual-review findings.
6. **Evidence, 1 minute:** inspect one stored patch and its check results. Show how
   a reader can trace a report finding back to concrete files.
7. **Next steps, 1 minute:** propose client-representative benchmark tasks and a
   controlled live evaluation before drawing rollout conclusions.

## PowerShell commands for this checkout

Run from your `agent-eval-lab` checkout. These commands use the existing virtual environment.

```powershell
.\.venv\Scripts\agent-eval.exe version
.\.venv\Scripts\agent-eval.exe tasks -b benchmarks/py-customers
.\.venv\Scripts\agent-eval.exe doctor -b benchmarks/py-customers
.\.venv\Scripts\agent-eval.exe evaluate -c examples/live-demo.yaml
```

`evaluate` also runs benchmark validation automatically. Open the exact
`report.html` path printed at completion in a browser. Use the printed evaluation ID
for the remaining commands. The expected demo verdict is `NEGATIVE`: the candidate's
correctness improvement is uncertain with one repetition, while its simulated cost and
duration exceed the configured guardrails. This is useful because it demonstrates that
the decision follows declared gates rather than selecting the most favorable metric.

To rebuild a specific evaluation without rerunning the agent:

```powershell
.\.venv\Scripts\agent-eval.exe report -c examples/live-demo.yaml -e <evaluation-id>
```

To inspect one run and its patch:

```powershell
.\.venv\Scripts\agent-eval.exe show t02-fix-lookup-bug-candidate-rep01 -c examples/live-demo.yaml -e <evaluation-id> --diff
```

Replace `<evaluation-id>` with the generated folder name. Explicit selection avoids
accidentally presenting a different evaluation when several exist.

Use `examples/demo.yaml` after the presentation when you need the full three-repetition,
30-run comparison. Its larger sample gives a more useful reliability estimate and tighter
uncertainty bounds, but it takes longer and is less convenient for a live walkthrough.

## Where things live

| Location | Responsibility |
|---|---|
| `src/agent_eval/cli.py` | CLI commands and workflow orchestration |
| `config.py`, `models.py` | Validated settings and stage-boundary data models |
| `benchmark.py`, `doctor.py` | Benchmark loading and validation |
| `harness.py`, `workspace.py` | Harness identity, comparison, and temporary workspaces |
| `execution.py`, `runners/` | Execution and simulated/live/replay adapters |
| `checks/` | Objective verification subprocesses |
| `judge/`, `judging.py` | Rubrics, providers, and stored-patch judging |
| `metrics.py`, `stats.py`, `decide.py` | Aggregation, uncertainty, and verdict rules |
| `pipeline.py`, `report/` | Final report assembly and HTML rendering |
| `store.py`, `redact.py`, `env.py` | Persistence, redaction, and environment handling |
| `benchmarks/`, `harnesses/`, `examples/` | Experiment inputs |
| `tests/` | Evaluator regression and behavior tests |
| `docs/` | Architecture, decisions, manual checks, and development history |
| `skills/` | Written procedures for review, regression investigation, task creation |
| `runs/` | Generated evidence and reports; excluded from Git |

Each evaluation saves metadata, a run plan, per-run JSON/logs/patches/checks/judgments,
and summary and report files. SQLite is a rebuildable index; artifact files hold
the authoritative run evidence.

## Scope to communicate accurately

The current package version is 0.1.0. It includes one small Python benchmark and
one live agent integration, plus offline simulation and replay. It runs sequentially
on one machine and uses the evaluator's Python environment for checks. A temporary
workspace is not a container security boundary.

There is no hosted dashboard, authentication system, distributed execution,
built-in resume/retry workflow, or human-calibrated judge. The small benchmark and
heuristic demo cannot establish production performance or client-specific ROI.

Useful next work is to add representative client tasks, agree on acceptance
thresholds, validate the benchmark, review provider/data access requirements, and
run the real comparison with enough coverage to support a decision.
