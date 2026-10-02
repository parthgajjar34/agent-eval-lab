# Agent Eval Lab — submission brief

## Concepts and why

**Harness:** instructions, skills, permissions, and model settings overlaid before an agent runs. It is identified by a content hash because behaviour matters more than repository history. **Benchmark task:** a prompt, fixture, hidden verification, rubric, protected paths, and a known-good reference. Hidden verification prevents the agent from reading its grader. **Run:** one task, harness, and repetition in a throwaway Git workspace. **Evaluation:** saved run artifacts transformed into checks, judgments, statistics, a decision, and a report. Files are the source of truth so reports can be rebuilt without rerunning agents.

## Five hardest decisions

1. Use ordered gates instead of a weighted score. Correctness, quality, cost, and reliability have no defensible exchange rate; a critical regression must be able to veto an average improvement.
2. Keep the judge blind to test results. Passing tests and a judge praising the tests would count the same evidence twice, so the API makes outcome contamination impossible.
3. Analyse tasks rather than pooled repetitions. Repetitions share difficulty; treating them as independent would make uncertainty look smaller than it is.
4. Hash harness content instead of using a Git SHA. Renaming a harness should not invalidate recordings, while an uncommitted behavioural edit must change its identity.
5. Use deterministic replay and real checks for the offline demo. It must be possible to inspect a complete evaluation without an API key, while every simulated value remains labelled as simulated.

## What was cut

Parallel execution, resume/retry, additional agent adapters, Docker isolation, per-task environments, pairwise judging, human judge calibration, trend tracking, a web UI, authentication, and a database server were cut to keep the six-to-eight-hour exercise focused. The trade-off is explicit in the report’s limitations; the next useful investment is calibrated human labels for the judge.

## A result I did not trust

An early `doctor` run said an untouched refactor fixture had changed. Investigation showed that pytest and mypy had created cache files before the non-empty-diff check, making a no-op look like an agent patch. I changed workspace creation to exclude tool caches from Git, added regression tests, and reran the benchmark. The current doctor run validates all five tasks. A second review found inconsistent judge thresholds; those thresholds now share one configuration source and the report has a middle band plus a manual-review queue.
