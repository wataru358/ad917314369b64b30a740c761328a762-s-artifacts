#!/usr/bin/env python3
"""Track the playbook; analysis is performed by the agent, never by this CLI."""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import uuid

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ is required. Select python3.11 or a newer interpreter.")

STATES = {"not_started", "in_progress", "blocked", "complete"}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".status-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def inside(base, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError(f"relative path required: {value!r}")
    resolved = (base / value).resolve()
    if not resolved.is_relative_to(base.resolve()):
        raise ValueError(f"path escapes its owner: {value}")
    return resolved


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def attempt_directory(root, config, row, story, require_exists=True):
    attempt = story.get("attempt")
    if not isinstance(attempt, str) or not re.fullmatch(r"[0-9a-f]{32}", attempt):
        raise ValueError("invalid attempt identity")
    expected = Path("runs") / config["run_id"] / row["branch"] / row["id"] / attempt
    if story.get("output_dir") != expected.as_posix():
        raise ValueError("output directory does not match run/task/attempt")
    path = root
    for part in expected.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("attempt directories must not contain symlinks")
    if require_exists and not path.is_dir():
        raise ValueError(f"active attempt output directory is missing: {expected.as_posix()}")
    return path


def load(root, allow_unsealed=False, recovering_task=None):
    config = read(root / "config.json")
    if config.get("profile") != "full":
        raise ValueError("tracked completion requires profile=full; probes are not completed studies")
    rows = read(root / "schedule.json")["tasks"]
    if {row["branch"] for row in rows} != {"download", "phase1", "phase2"}:
        raise ValueError("schedule must contain all three nonempty branches")
    seal_path = root / "run-lock.json"
    if seal_path.exists():
        seal = read(seal_path)
        if seal["run_id"] != config.get("run_id") or seal["config_sha256"] != digest(root / "config.json"):
            raise ValueError("initialized run/config changed")
        if seal["schedule_sha256"] != digest(root / "schedule.json"):
            raise ValueError("initialized task plan or criteria changed")
    elif config.get("run_id") and not allow_unsealed:
        raise ValueError("initialization incomplete; rerun init with the same run id")
    catalog = {row["id"]: row for row in rows}
    if len(catalog) != len(rows) or len({row["node"] for row in rows}) != len(rows):
        raise ValueError("duplicate task id or node")
    visiting, visited = set(), set()

    def visit(key):
        if key in visiting:
            raise ValueError(f"dependency cycle: {key}")
        if key in visited:
            return
        visiting.add(key)
        for dependency in catalog[key]["dependencies"]:
            if dependency not in catalog:
                raise ValueError(f"unknown dependency: {dependency}")
            visit(dependency)
        visiting.remove(key)
        visited.add(key)

    states = {}
    for key, row in catalog.items():
        visit(key)
        if len(Path(row["node"]).parts) != 2 or Path(row["node"]).parts[0] != row["branch"]:
            raise ValueError(f"task must be a third-level node: {key}")
        node = inside(root, row["node"])
        if Path(row["handoff"]).name != row["handoff"]:
            raise ValueError("handoff must be a filename owned by the leaf")
        for name in ("AGENT.md", row["handoff"], "status.json"):
            if not inside(node, name).is_file():
                raise ValueError(f"missing task file: {node / name}")
        record = read(node / "status.json")
        if len(record["user_stories"]) != 1:
            raise ValueError(f"leaf must have one story: {key}")
        story = record["user_stories"][0]
        if story["id"] != key or story["status"] not in STATES:
            raise ValueError(f"invalid leaf story: {key}")
        if record["status"] != story["status"]:
            raise ValueError(f"leaf record/story status differ: {key}")
        if type(story["passes"]) is not bool or story["passes"] != (story["status"] == "complete"):
            raise ValueError(f"passes/status disagree: {key}")
        expected = [f"C{i:02}" for i in range(1, len(row["acceptance_criteria"]) + 1)]
        if [criterion["id"] for criterion in story["acceptance_criteria"]] != expected:
            raise ValueError(f"criteria do not match schedule: {key}")
        if [c["criterion"] for c in story["acceptance_criteria"]] != row["acceptance_criteria"]:
            raise ValueError(f"criterion text changed: {key}")
        if any(type(c["met"]) is not bool for c in story["acceptance_criteria"]):
            raise ValueError(f"criterion met is not boolean: {key}")
        if story["status"] == "complete" and not all(c["met"] for c in story["acceptance_criteria"]):
            raise ValueError(f"complete task has unmet criteria: {key}")
        if story["status"] != "complete" and any(c["met"] for c in story["acceptance_criteria"]):
            raise ValueError(f"unfinished task claims met criteria: {key}")
        states[key] = record
    for key, record in states.items():
        story = record["user_stories"][0]
        if story["status"] in {"in_progress", "complete"}:
            if not nonblank(story.get("owner")) or not story.get("attempt") or not story.get("output_dir"):
                raise ValueError(f"task has no owner/attempt/output: {key}")
            attempt_directory(root, config, catalog[key], story,
                              require_exists=not (recovering_task is not None and story["status"] == "in_progress"))
            if any(states[d]["user_stories"][0]["status"] != "complete" for d in catalog[key]["dependencies"]):
                raise ValueError(f"task ran before its dependencies: {key}")
        if story["status"] == "complete":
            receipt = inside(root, story.get("receipt", ""))
            if digest(receipt) != story.get("receipt_sha256"):
                raise ValueError(f"receipt changed: {key}")
            verify_receipt(root, config, catalog[key], story, receipt)
    if config.get("run_id") and not seal_path.exists() and any(
        record["user_stories"][0]["status"] != "not_started" for record in states.values()
    ):
        raise ValueError("unsealed run already contains work; restore initialization evidence")
    return config, catalog, states


def verify_receipt(root, config, row, story, receipt_path):
    output = attempt_directory(root, config, row, story)
    if not receipt_path.is_relative_to(output):
        raise ValueError("receipt must be inside this attempt output directory")
    receipt = read(receipt_path)
    for field, expected in [("task_id", row["id"]), ("run_id", config["run_id"]),
                            ("attempt", story["attempt"]), ("scope", "full")]:
        if receipt.get(field) != expected:
            raise ValueError(f"receipt {field} mismatch")
    verification = receipt.get("verification", {})
    if not isinstance(verification, dict):
        raise ValueError("verification must be a record")
    if type(verification.get("exit_code")) is not int or verification["exit_code"] != 0:
        raise ValueError("successful verification exit_code required")
    if not nonblank(verification.get("summary")) or not nonblank(verification.get("reviewer")):
        raise ValueError("verification summary and independent reviewer required")
    if verification["reviewer"].strip().casefold() == story["owner"].strip().casefold():
        raise ValueError("owner cannot be its own independent reviewer")
    artifacts = receipt.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts or any(not isinstance(a, dict) for a in artifacts):
        raise ValueError("artifacts must be a nonempty list of records")
    names = [entry["path"] for entry in artifacts]
    if len(names) != len(set(names)):
        raise ValueError("duplicate receipt artifact")
    if not set(row["outputs"]).issubset(names):
        raise ValueError(f"missing declared outputs: {set(row['outputs']) - set(names)}")
    for artifact in artifacts:
        if not nonblank(artifact.get("path")) or not isinstance(artifact.get("sha256"), str):
            raise ValueError("artifact path and sha256 must be strings")
        if not re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]):
            raise ValueError("artifact sha256 must be 64 lowercase hexadecimal characters")
        path = inside(output, artifact["path"])
        if not path.is_file() or digest(path) != artifact.get("sha256"):
            raise ValueError(f"missing or changed artifact: {artifact['path']}")
    criteria = receipt.get("criteria", [])
    if not isinstance(criteria, list) or any(not isinstance(c, dict) for c in criteria):
        raise ValueError("criteria must be a list of records")
    expected = [criterion["id"] for criterion in story["acceptance_criteria"]]
    if [criterion.get("id") for criterion in criteria] != expected:
        raise ValueError("receipt criteria differ from task criteria")
    for criterion in criteria:
        evidence = criterion.get("evidence")
        if criterion.get("passed") is not True or not isinstance(evidence, list) or not evidence:
            raise ValueError(f"criterion has no successful evidence: {criterion.get('id')}")
        if any(not nonblank(path) or path not in names for path in evidence):
            raise ValueError("criterion evidence must name hashed artifacts")


def aggregate(statuses):
    if all(status == "complete" for status in statuses):
        return "complete"
    if "in_progress" in statuses:
        return "in_progress"
    if "blocked" in statuses:
        return "blocked"
    return "in_progress" if "complete" in statuses else "not_started"


def sync(root, catalog, states, check=False):
    branch_records = {}
    for branch in ("download", "phase1", "phase2"):
        path = root / branch / "status.json"
        record = read(path)
        rows = [row for row in catalog.values() if row["branch"] == branch]
        if [story["id"] for story in record["user_stories"]] != [row["id"] for row in rows]:
            raise ValueError(f"branch task list differs: {branch}")
        for story in record["user_stories"]:
            if len(story["acceptance_criteria"]) != 1:
                raise ValueError("branch rollup requires one child-completion criterion")
            child = states[story["id"]]["user_stories"][0]
            if check and (story["status"], story["passes"]) != (child["status"], child["passes"]):
                raise ValueError(f"stale branch rollup: {branch}")
            if check and any(c["met"] is not child["passes"] for c in story["acceptance_criteria"]):
                raise ValueError(f"stale branch criterion: {branch}")
            story["status"], story["passes"] = child["status"], child["passes"]
            for criterion in story["acceptance_criteria"]:
                criterion["met"] = child["passes"]
        computed = aggregate([story["status"] for story in record["user_stories"]])
        if check and record["status"] != computed:
            raise ValueError(f"stale branch status: {branch}")
        record["status"] = computed
        branch_records[branch] = record
        if not check:
            record["updated_at"] = now()
            write(path, record)
    path = root / "status.json"
    record = read(path)
    if [story["id"] for story in record["user_stories"]] != ["download", "phase1", "phase2"]:
        raise ValueError("root must track exactly the three branches")
    for story in record["user_stories"]:
        if len(story["acceptance_criteria"]) != 1:
            raise ValueError("root rollup requires one branch-completion criterion")
        status = branch_records[story["id"]]["status"]
        passes = status == "complete"
        if check and (story["status"], story["passes"]) != (status, passes):
            raise ValueError("stale root rollup")
        if check and any(c["met"] is not passes for c in story["acceptance_criteria"]):
            raise ValueError("stale root criterion")
        story["status"], story["passes"] = status, passes
        for criterion in story["acceptance_criteria"]:
            criterion["met"] = passes
    computed = aggregate([story["status"] for story in record["user_stories"]])
    if check and record["status"] != computed:
        raise ValueError("stale root status")
    record["status"] = computed
    if not check:
        record["updated_at"] = now()
        write(path, record)
    return computed


@contextlib.contextmanager
def locked(root):
    with (root / ".state.lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def task_view(row, states):
    return {"id": row["id"], "node": row["node"], "handoff": f"{row['node']}/{row['handoff']}",
            **states[row["id"]]["user_stories"][0],
            "upstream": {d: states[d]["user_stories"][0].get("output_dir") for d in row["dependencies"]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("next", "status", "validate", "sync"):
        commands.add_parser(name)
    init = commands.add_parser("init")
    init.add_argument("--run-id", required=True)
    start = commands.add_parser("start")
    start.add_argument("task")
    start.add_argument("--owner", required=True)
    finish = commands.add_parser("finish")
    finish.add_argument("task")
    finish.add_argument("--evidence", required=True)
    for name in ("block", "retry"):
        sub = commands.add_parser(name)
        sub.add_argument("task")
        sub.add_argument("--reason", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    resuming = False
    with locked(root):
        config, catalog, states = load(root, allow_unsealed=args.command == "init",
                                      recovering_task=args.task if args.command == "block" else None)
        if args.command == "init":
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,80}", args.run_id):
                raise ValueError("invalid run id")
            if config.get("run_id") not in (None, args.run_id):
                raise ValueError("different run already exists; copy a fresh playbook for a new run")
            if config.get("run_id") is None and any(s["user_stories"][0]["status"] != "not_started" for s in states.values()):
                raise ValueError("cannot initialize changed task state")
            config["run_id"] = args.run_id
            write(root / "config.json", config)
            if not (root / "run-lock.json").exists():
                write(root / "run-lock.json", {"run_id": args.run_id, "initialized_at": now(),
                    "config_sha256": digest(root / "config.json"),
                    "schedule_sha256": digest(root / "schedule.json")})
        elif args.command in {"start", "finish", "block", "retry"}:
            if not config.get("run_id"):
                raise ValueError("run workflow.py init --run-id ... first")
            if args.task not in catalog:
                raise ValueError("unknown task id")
            row = catalog[args.task]
            record = states[args.task]
            story = record["user_stories"][0]
            if args.command == "start":
                if not nonblank(args.owner):
                    raise ValueError("owner must not be empty or whitespace")
                args.owner = args.owner.strip()
                if story["status"] == "in_progress" and story["owner"] == args.owner:
                    resuming = True
                else:
                    if story["status"] != "not_started":
                        raise ValueError("task is owned, blocked, or complete; do not start it again")
                    if any(states[d]["user_stories"][0]["status"] != "complete" for d in row["dependencies"]):
                        raise ValueError("dependencies are incomplete")
                    attempt = uuid.uuid4().hex
                    output = f"runs/{config['run_id']}/{row['branch']}/{row['id']}/{attempt}"
                    attempt_directory(root, config, row, {"attempt": attempt, "output_dir": output},
                                      require_exists=False).mkdir(parents=True, exist_ok=False)
                    story.update(status="in_progress", owner=args.owner, attempt=attempt,
                                 output_dir=output, started_at=now(), blocker=None)
            elif args.command == "finish":
                if story["status"] != "in_progress":
                    raise ValueError("only an in-progress task can finish")
                receipt = inside(root, args.evidence)
                verify_receipt(root, config, row, story, receipt)
                story.update(status="complete", passes=True, finished_at=now(),
                             receipt=args.evidence, receipt_sha256=digest(receipt), blocker=None)
                for criterion in story["acceptance_criteria"]:
                    criterion["met"] = True
            elif args.command == "block":
                if story["status"] == "complete" or not args.reason.strip():
                    raise ValueError("cannot block completed work or omit a reason")
                story.update(status="blocked", blocker=args.reason)
            else:
                if story["status"] != "blocked" or not args.reason.strip():
                    raise ValueError("retry requires a blocked task and a reason")
                story.setdefault("previous_attempts", []).append({k: story.get(k) for k in
                    ("attempt", "owner", "output_dir", "blocker")})
                story.update(status="not_started", owner=None, attempt=None, output_dir=None,
                             blocker=None, retry_reason=args.reason)
            record["status"] = story["status"]
            record["updated_at"] = now()
            write(inside(root, row["node"]) / "status.json", record)
        if args.command == "validate":
            status = sync(root, catalog, states, check=True)
        else:
            status = sync(root, catalog, states)
        tasks = [task_view(row, states) for row in catalog.values()]
        if args.command == "start":
            print(json.dumps({"action": "resume" if resuming else "started", "pipeline_status": status,
                              **task_view(catalog[args.task], states)}, ensure_ascii=False, indent=2))
        elif args.command == "next":
            active = [task for task in tasks if task["status"] == "in_progress"]
            ready = [task for task in tasks if task["status"] == "not_started" and
                     all(states[d]["user_stories"][0]["status"] == "complete" for d in catalog[task["id"]]["dependencies"])]
            print(json.dumps({"status": status, "resume": active, "ready": ready,
                              "blocked": [task for task in tasks if task["status"] == "blocked"]}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"valid": True, "status": status, "run_id": config.get("run_id"),
                              "complete_tasks": sum(task["passes"] for task in tasks),
                              "total_tasks": len(tasks), "tasks": tasks if args.command == "status" else []},
                             ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
