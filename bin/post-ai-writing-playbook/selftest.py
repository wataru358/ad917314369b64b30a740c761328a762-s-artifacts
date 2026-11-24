#!/usr/bin/env python3
"""Exercise state transitions in temporary synthetic projects, without network or real tasks."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ is required. Select python3.11 or a newer interpreter.")

HERE = Path(__file__).resolve().parent
CHECKS = []


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def story(key):
    return {"id": key, "title": key, "priority": 1, "status": "not_started", "passes": False,
            "acceptance_criteria": [{"id": "C01", "criterion": "synthetic check", "met": False}]}


def fixture(root):
    save(root / "config.json", {"profile": "full", "run_id": None})
    tasks = []
    for branch, key, dependencies in [("download", "D01", []), ("phase1", "T00", ["D01"]),
                                       ("phase2", "P2-S01", ["T00"])]:
        node = f"{branch}/test"
        task = {"id": key, "node": node, "branch": branch, "dependencies": dependencies,
                "handoff": "handoff.md", "outputs": ["report.md", "manifest.json", "verification.json"],
                "acceptance_criteria": ["synthetic check"]}
        tasks.append(task)
        save(root / node / "status.json", {"status": "not_started", "user_stories": [story(key)]})
        for name in ("AGENT.md", "handoff.md"):
            (root / node / name).write_text("Synthetic fixture only.\n", encoding="utf-8")
        save(root / branch / "status.json", {"status": "not_started", "user_stories": [story(key)]})
    save(root / "schedule.json", {"tasks": tasks})
    save(root / "status.json", {"status": "not_started", "user_stories":
                                [story(key) for key in ("download", "phase1", "phase2")]})


def command(root, *args, expect=0, label=None, error_contains=None):
    process = subprocess.run([sys.executable, "-B", str(HERE / "workflow.py"), "--root", str(root), *args],
                             text=True, capture_output=True)
    assert process.returncode == expect, (args, process.returncode, process.stdout, process.stderr)
    value = json.loads(process.stdout if expect == 0 else process.stderr)
    if error_contains:
        assert error_contains in value.get("error", ""), (args, value)
    if label:
        CHECKS.append({"check": label, "result": "PASS", "exit_code": process.returncode})
    return value


def task_state(root, key):
    task = next(row for row in read(root / "schedule.json")["tasks"] if row["id"] == key)
    return task, read(root / task["node"] / "status.json")["user_stories"][0]


def receipt(root, key):
    task, state = task_state(root, key)
    output = root / state["output_dir"]
    for filename in task["outputs"]:
        (output / filename).write_text("Synthetic verification fixture, not research.\n", encoding="utf-8")
    proof = {"task_id": key, "run_id": "synthetic-run", "attempt": state["attempt"], "scope": "full",
             "verification": {"exit_code": 0, "reviewer": "synthetic-reviewer", "summary": "fixture only"},
             "criteria": [{"id": "C01", "passed": True, "evidence": ["report.md"]}],
             "artifacts": [{"path": filename, "sha256": hashlib.sha256((output / filename).read_bytes()).hexdigest()}
                           for filename in task["outputs"]]}
    path = output / "receipt.json"
    save(path, proof)
    return path, proof


def main():
    with tempfile.TemporaryDirectory(prefix="post-ai-playbook-selftest-") as temporary:
        root = Path(temporary) / "original"
        fixture(root)
        command(root, "validate", label="fresh fixture validates with zero completed tasks")
        command(root, "start", "D01", "--owner", "one", expect=1, label="start requires initialized run")
        command(root, "init", "--run-id", "synthetic-run")
        command(root, "start", "D01", "--owner", " ", expect=1,
                error_contains="owner must not be empty", label="blank owner rejected without changing state")
        assert task_state(root, "D01")[1]["status"] == "not_started"
        command(root, "init", "--run-id", "different", expect=1, label="run identity cannot silently change")
        command(root, "start", "T00", "--owner", "one", expect=1, label="unfinished dependency rejects start")
        ready = command(root, "next")
        assert [item["id"] for item in ready["ready"]] == ["D01"]
        CHECKS.append({"check": "next selects only dependency-ready work", "result": "PASS"})
        processes = [subprocess.Popen([sys.executable, "-B", str(HERE / "workflow.py"), "--root", str(root),
                                        "start", "D01", "--owner", owner], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True) for owner in ("first", "second")]
        outputs = [process.communicate() for process in processes]
        assert sorted(process.returncode for process in processes) == [0, 1], outputs
        winner = json.loads(outputs[next(i for i, process in enumerate(processes) if process.returncode == 0)][0])
        assert winner["action"] == "started" and winner["output_dir"] and winner["attempt"] and winner["handoff"]
        CHECKS.append({"check": "new start returns its attempt, handoff and output directory", "result": "PASS"})
        CHECKS.append({"check": "concurrent claims have exactly one owner", "result": "PASS"})
        _, active = task_state(root, "D01")
        stale = read(root / "download/status.json")
        stale["status"] = "not_started"
        stale["user_stories"][0]["status"] = "not_started"
        save(root / "download/status.json", stale)
        resumed = command(root, "start", "D01", "--owner", active["owner"])
        assert resumed["action"] == "resume" and resumed["attempt"] == active["attempt"]
        command(root, "validate", label="same-owner resume repairs a stale parent rollup")
        saved_config = (root / "config.json").read_bytes()
        changed_config = read(root / "config.json")
        changed_config["run_id"] = "changed-run"
        save(root / "config.json", changed_config)
        command(root, "validate", expect=1, error_contains="run/config changed",
                label="run identity and configuration stay sealed")
        (root / "config.json").write_bytes(saved_config)
        CHECKS.append({"check": "same-owner resume preserves attempt and checkpoint directory", "result": "PASS"})
        command(root, "finish", "D01", "--evidence", "missing.json", expect=1,
                label="missing receipt cannot complete work")
        proof_path, original = receipt(root, "D01")
        relative = str(proof_path.relative_to(root))
        for label, mutate in [
            ("failed criterion rejected", lambda p: p["criteria"][0].update(passed=False)),
            ("missing declared output rejected", lambda p: p["artifacts"].pop()),
            ("self review rejected", lambda p: p["verification"].update(reviewer=active["owner"])),
            ("whitespace and case do not disguise self review", lambda p: p["verification"].update(reviewer=" " + active["owner"].upper() + " ")),
            ("nonzero verification rejected", lambda p: p["verification"].update(exit_code=1)),
            ("pilot receipt rejected for full study", lambda p: p.update(scope="pilot")),
            ("wrong attempt rejected", lambda p: p.update(attempt="stale")),
            ("path traversal rejected", lambda p: p["artifacts"].append({"path": "../escape", "sha256": "0" * 64})),
            ("nonstring reviewer rejected", lambda p: p["verification"].update(reviewer=True)),
            ("nonstring summary rejected", lambda p: p["verification"].update(summary=["bad"])),
            ("nonlist evidence rejected", lambda p: p["criteria"][0].update(evidence={"report.md": True})),
        ]:
            changed = json.loads(json.dumps(original))
            mutate(changed)
            save(proof_path, changed)
            command(root, "finish", "D01", "--evidence", relative, expect=1, label=label)
        save(proof_path, original)
        output = proof_path.parent
        alias = output.with_name(output.name + "-preserved")
        output.rename(alias)
        output.symlink_to(alias, target_is_directory=True)
        command(root, "validate", expect=1, error_contains="symlinks",
                label="an attempt cannot alias another directory")
        output.unlink()
        alias.rename(output)
        command(root, "finish", "D01", "--evidence", relative, label="valid artifact receipt finishes leaf")
        assert read(root / "download/status.json")["status"] == "complete"
        assert read(root / "status.json")["status"] != "complete"
        CHECKS.append({"check": "parent rollup does not finish unrelated work", "result": "PASS"})
        artifact = proof_path.parent / "report.md"
        previous = artifact.read_bytes()
        artifact.write_text("mutated", encoding="utf-8")
        command(root, "validate", expect=1, label="changed output invalidates prior completion")
        artifact.write_bytes(previous)
        top = read(root / "status.json")
        top["user_stories"][1]["passes"] = True
        save(root / "status.json", top)
        command(root, "validate", expect=1, label="stale parent completion rejected")
        command(root, "sync", label="parent rollup repairs from leaf truth")
        saved_schedule = (root / "schedule.json").read_bytes()
        changed_schedule = read(root / "schedule.json")
        changed_schedule["tasks"][0]["acceptance_criteria"][0] = "weakened after completion"
        save(root / "schedule.json", changed_schedule)
        command(root, "validate", expect=1, error_contains="task plan or criteria changed",
                label="acceptance criteria stay sealed after initialization")
        (root / "schedule.json").write_bytes(saved_schedule)
        command(root, "start", "T00", "--owner", "phase1-worker")
        _, old_state = task_state(root, "T00")
        command(root, "block", "T00", "--reason", "synthetic missing input")
        command(root, "retry", "T00", "--reason", "input restored and old worker confirmed stopped")
        command(root, "start", "T00", "--owner", "phase1-new")
        _, new_state = task_state(root, "T00")
        assert old_state["output_dir"] != new_state["output_dir"] and (root / old_state["output_dir"]).exists()
        CHECKS.append({"check": "retry isolates a new attempt and preserves old artifacts", "result": "PASS"})
        for key, owner in [("T00", None), ("P2-S01", "phase2-worker")]:
            if owner:
                command(root, "start", key, "--owner", owner)
            path, proof = receipt(root, key)
            command(root, "finish", key, "--evidence", str(path.relative_to(root)))
        final = command(root, "validate")
        assert final["status"] == "complete" and final["complete_tasks"] == 3
        CHECKS.append({"check": "root completes only after all leaves complete", "result": "PASS"})
        relocated = Path(temporary) / "relocated"
        shutil.copytree(root, relocated)
        command(relocated, "validate", label="relative evidence survives relocation")
        fresh = Path(temporary) / "negative-plan"
        fixture(fresh)
        broken = read(fresh / "schedule.json")
        broken["tasks"][0]["dependencies"] = ["P2-S01"]
        save(fresh / "schedule.json", broken)
        command(fresh, "validate", expect=1, error_contains="dependency cycle", label="dependency cycle rejected")
        fixture(fresh)
        broken = read(fresh / "schedule.json")
        broken["tasks"] = broken["tasks"][:-1]
        save(fresh / "schedule.json", broken)
        command(fresh, "validate", expect=1, error_contains="three nonempty branches",
                label="an empty phase cannot become complete")
        fixture(fresh)
        broken = read(fresh / "schedule.json")
        broken["tasks"][0]["handoff"] = "../../../outside.md"
        save(fresh / "schedule.json", broken)
        command(fresh, "next", expect=1, error_contains="handoff must be a filename",
                label="handoff cannot escape its leaf")
        fixture(fresh)
        command(fresh, "init", "--run-id", "synthetic-run")
        command(fresh, "start", "D01", "--owner", "missing-output-worker")
        _, missing = task_state(fresh, "D01")
        (fresh / missing["output_dir"]).rmdir()
        command(fresh, "next", expect=1, error_contains="output directory is missing",
                label="missing active output is not offered as valid resume")
        command(fresh, "block", "D01", "--reason", "active output lost; old worker stopped")
        command(fresh, "retry", "D01", "--reason", "recover in a fresh isolated attempt")
        command(fresh, "start", "D01", "--owner", "recovery-worker",
                label="missing active output still permits block and retry recovery")
        interrupted = Path(temporary) / "interrupted-init"
        fixture(interrupted)
        interrupted_config = read(interrupted / "config.json")
        interrupted_config["run_id"] = "synthetic-run"
        save(interrupted / "config.json", interrupted_config)
        command(interrupted, "validate", expect=1, error_contains="initialization incomplete",
                label="an interrupted initialization is detected")
        command(interrupted, "init", "--run-id", "synthetic-run")
        command(interrupted, "validate", label="same-run init recovers a partial initialization")
        multiple = Path(temporary) / "multiple-missing"
        fixture(multiple)
        plan = read(multiple / "schedule.json")
        plan["tasks"][1]["dependencies"] = []
        save(multiple / "schedule.json", plan)
        command(multiple, "init", "--run-id", "synthetic-run")
        for key in ["D01", "T00"]:
            command(multiple, "start", key, "--owner", "missing-" + key)
        for key in ["D01", "T00"]:
            (multiple / task_state(multiple, key)[1]["output_dir"]).rmdir()
        for key in ["D01", "T00"]:
            command(multiple, "block", key, "--reason", "all old workers stopped, output directories lost")
        command(multiple, "retry", "D01", "--reason", "start a fresh attempt")
        command(multiple, "start", "D01", "--owner", "recovered-D01",
                label="several missing active outputs can be blocked and recovered")
        example = subprocess.run([sys.executable, "-B", str(HERE / "example_measure.py")],
                                 text=True, capture_output=True, check=True)
        rows = [json.loads(line) for line in example.stdout.splitlines()]
        assert rows[0]["phase1_subset"]["M05_list_share_S"] == 0.2
        assert rows[0]["phase2"]["P2-M05"] == 0.25
        assert rows[1]["phase2"]["P2-M05"] is None
        assert rows[1]["phase2"]["P2-M04"] == 0
        CHECKS.append({"check": "example distinguishes phase denominators, zero and NA", "result": "PASS"})
    print(json.dumps({"status": "PASS", "checks": CHECKS, "research_executed": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
