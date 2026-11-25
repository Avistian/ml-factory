"""tests/test_workflows.py: compute only happens in agent-train.yml (ADR 0004)."""

import pathlib
import re

WF = pathlib.Path(__file__).resolve().parents[1] / ".github/workflows"
FORBIDDEN = re.compile(r"modal|make train|make data|make eval\b(?!-)", re.IGNORECASE)


def test_only_the_train_workflow_mentions_compute() -> None:
    for f in WF.glob("*.yml"):
        if f.name == "agent-train.yml":
            continue
        assert not FORBIDDEN.search(f.read_text()), f"{f.name} must not start compute"


def test_train_workflow_never_runs_on_pull_requests() -> None:
    text = (WF / "agent-train.yml").read_text()
    assert "pull_request" not in text


def workflow_jobs(text: str) -> list[str]:
    """Split job mappings without adding a YAML dependency."""
    return re.split(r"(?m)^  [\w-]+:\s*$", text.split("\njobs:\n", 1)[1])[1:]


def test_codex_jobs_use_local_cli_and_runner() -> None:
    count = 0
    for f in WF.glob("*.yml"):
        text = f.read_text()
        assert "OPENAI_API_KEY" not in text
        assert "openai/codex-action" not in text
        for job in workflow_jobs(text):
            if "id: run_codex" not in job:
                continue
            count += 1
            assert "runs-on: [self-hosted, codex]" in job
            assert "command -v codex" in job
            assert "codex --ask-for-approval never exec --sandbox workspace-write" in job
            assert "< .sandcastle/agent-workflows/" in job
    assert count == 5


def test_non_agent_checks_stay_hosted() -> None:
    for name in ("agent-train",):
        for job in workflow_jobs((WF / f"{name}.yml").read_text()):
            assert "runs-on: ubuntu-latest" in job


def test_self_hosted_pull_requests_reject_forks() -> None:
    for f in WF.glob("*.yml"):
        text = f.read_text()
        assert not re.search(r"^  pull_request_target:", text, re.M)
        if f.name != "agent-review.yml":
            continue
        for job in workflow_jobs(text):
            if "self-hosted" in job:
                condition = job.split("    steps:", 1)[0]
                assert (
                    "github.event.pull_request.head.repo.full_name == github.repository"
                    in condition
                )


def test_implement_commits_after_codex_with_hook() -> None:
    for name in ("agent-implement", "agent-implement-spec"):
        jobs = workflow_jobs((WF / f"{name}.yml").read_text())
        job = next(j for j in jobs if "name: Build the ticket" in j)
        assert job.index("id: run_codex") < job.index("name: Commit the changes")
        commit = job.split("name: Commit the changes", 1)[1].split("      - name:", 1)[0]
        assert "git add -A" in commit
        assert "git diff --cached --quiet" in commit
        assert "git commit -m" in commit
        assert "--no-verify" not in commit
        assert "core.hooksPath" not in commit


def test_workflows_never_use_pr_edit() -> None:
    for f in WF.iterdir():
        if f.suffix in {".yml", ".yaml"}:
            assert not re.search(r"\bgh\s+pr\s+edit\b", f.read_text()), f.name



def test_reusable_interfaces_and_guards() -> None:
    for f in WF.glob("agent-*.yml"):
        text = f.read_text()
        assert "  workflow_call:" in text
        assert "      FACTORY_PAT:\n        required: true" in text
        assert "  group: reusable-" in text
        gate = "COMPUTE_ENABLED" if f.stem == "agent-train" else "FACTORY_ENABLED"
        assert f"vars.{gate} == 'true'" in text
    for name in ("agent-implement", "agent-implement-spec"):
        text = (WF / f"{name}.yml").read_text()
        assert 'if [ "$open" -ge 3 ]; then' in text
        assert "gh run list" not in text
        assert "steps.caps.outputs.allowed == 'true'" in text


def test_generation_requires_reservation_and_cpu_smoke_before_credentials() -> None:
    text = (WF / "agent-train.yml").read_text()
    reserve = text.index("- name: Reserve generation budget")
    smoke = text.index("- name: Generation CPU smoke")
    launch = text.index("- name: Generate and verify durable resume on Modal")
    assert reserve < smoke < launch
    assert "MODAL_TOKEN" not in text[reserve:launch]
    assert "check_generation_caps.py" in text[reserve:smoke]
    assert "--limit 1000" in text[reserve:smoke]
    assert "if: always() && inputs.mode == 'generation'" in text[launch:]


def test_generation_does_not_enter_training_or_benchmark_steps() -> None:
    text = (WF / "agent-train.yml").read_text()
    steps = text.split("      - name: ")[1:]
    for step in steps:
        if any(command in step for command in ("make data", "make eval-smoke", "modal_train.py",
                                               "r0 leaderboard", "gh pr create")):
            assert "if: inputs.mode == 'train'" in step
