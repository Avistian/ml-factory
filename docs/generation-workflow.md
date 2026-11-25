# Guarded generation

The existing `agent-train.yml` reusable workflow accepts `mode: generation`.
Its default remains `train`. Generation calls the consumer's scripts:

1. `check_generation_caps.py` validates config and current workflow history and writes
   a reservation before credentials become available. It must reject workflow reruns
   (`GITHUB_RUN_ATTEMPT != 1`), over-budget requests and incomplete history.
2. `generate.py` executes a small local CPU smoke.
3. `modal_generate.py` uses the reservation, then verifies persisted output by resuming
   in another container. Only this step receives Modal credentials.

Generation does not download benchmarks, train a model or write leaderboard rows.
An always-run artifact step retains available reservation, local smoke and hosted
outcome files, including failed or uncertain attempts. A reservation is not billing.

Required repository variables: `COMPUTE_ENABLED`, `MAX_TRAIN_RUNS_PER_DAY`, `MAX_GPU`,
`MAX_GENERATION_TASKS`, `MAX_GENERATION_SECONDS`, `MAX_GENERATION_BYTES`,
`GENERATION_RUN_RESERVATION_USD`, and `GENERATION_DAILY_BUDGET_USD`.
`GENERATION_JOB_TIMEOUT_MINUTES` defaults to 15 and must be validated by the consumer
against its generation, resume and startup time allowances. Credentials remain in
Actions secrets. The consuming caller needs `actions: read` for admission history.

These controls do not provide a provider-enforced dollar cap. Image builds and
infrastructure retries are separately chargeable. Follow the consumer's authorization
and dashboard-budget policy; do not treat configuration alone as launch permission.

Verify this workflow's contracts with `python -m pytest tests/test_workflows.py`.
Actual provider behavior requires a separately authorized hosted run.
