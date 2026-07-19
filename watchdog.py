#!/usr/bin/env python3
"""Dental AI - Hermes/Kilo collaboration watchdog.

Polls the remote repo for new branches + status changes and reacts
to phase transitions defined in ``status.yaml`` without user intervention.
"""

from __future__ import annotations

import subprocess
import time
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
STATUS_FILE = REPO_ROOT / "status.yaml"
MESSAGES_FILE = REPO_ROOT / "messages.md"
REMOTE = "ericecek"
POLL_INTERVAL = 180  # 3 minutes
TRIGGER_BRANCH = "improve-precision-v1"


def log(msg: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] {msg}", flush=True)


def sh(cmd: list[str], cwd: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=False,
    )
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    if result.returncode != 0:
        log(f"CMD FAIL: {' '.join(cmd)} :: {err}")
    return out


def git_fetch() -> bool:
    out = sh(["git", "fetch", REMOTE])
    if "fatal" in out.lower() or "error" in out.lower():
        return False
    return True


def branch_exists_on_remote(name: str) -> bool:
    out = sh(["git", "ls-remote", "--heads", REMOTE, name])
    return bool(out)


def current_branch() -> str | None:
    out = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return out or None


def switch_branch(name: str) -> bool:
    cur = current_branch()
    if cur == name:
        return True
    out = sh(["git", "checkout", name])
    return "error" not in out.lower() and "fatal" not in out.lower()


def pull_rebase(branch: str = "main") -> bool:
    fetch_ok = git_fetch()
    if not fetch_ok:
        log("Fetch failed; skipping pull.")
        return False
    out = sh(["git", "pull", "--rebase", REMOTE, branch])
    if "CONFLICT" in out or "error" in out.lower():
        log("Rebase conflict or error; aborting safely.")
        sh(["git", "rebase", "--abort"])
        return False
    return True


def read_status() -> dict:
    if not STATUS_FILE.exists():
        return {}
    try:
        import yaml  # type: ignore

        return yaml.safe_load(STATUS_FILE.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        log(f"status.yaml parse error: {exc}")
        return {}


def write_status(data: dict) -> None:
    try:
        import yaml  # type: ignore

        STATUS_FILE.write_text(
            yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
    except Exception as exc:
        log(f"status.yaml write error: {exc}")


def append_message(text: str) -> None:
    if not MESSAGES_FILE.exists():
        MESSAGES_FILE.write_text(
            "# Správy medzi agentami\n\n## Formát\n```\n[ČAS] AGENT: SPRÁVA\n```\n\n## História\n\n", encoding="utf-8"
        )
    stamp = datetime.now(timezone.utc).strftime("[%Y-%m-%d %H:%M]")
    MESSAGES_FILE.write_text(MESSAGES_FILE.read_text(encoding="utf-8") + f"{stamp} {text}\n\n", encoding="utf-8")


def commit_and_push(files: list[str], message: str) -> bool:
    for f in files:
        out = sh(["git", "add", f])
        if out and "error" in out.lower():
            log(f"git add error for {f}: {out}")
            return False
    out = sh(["git", "commit", "-m", message])
    if "nothing to commit" in out.lower() or "no changes" in out.lower():
        return True
    if "error" in out.lower():
        return False
    out = sh(["git", "push", REMOTE, current_branch() or "main"])
    return "error" not in out.lower() and "fatal" not in out.lower()


def run_setup() -> bool:
    setup = REPO_ROOT / "setup_local.py"
    if not setup.exists():
        log("setup_local.py missing, skipping.")
        return False
    log("Running setup_local.py ...")
    result = subprocess.run(
        [sys.executable, str(setup)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    log(f"setup rc={result.returncode}")
    if result.stdout:
        log(result.stdout[:1200])
    if result.returncode != 0:
        log(result.stderr[-1200:] if result.stderr else "")
    return result.returncode == 0


def run_training(model: str = "yolov8") -> bool:
    script = REPO_ROOT / ("train_yolo8_local.py" if model == "yolov8" else "train_yolo11_local.py")
    if not script.exists():
        log(f"{script} missing.")
        return False
    log(f"Starting training: {script}")
    log_file = REPO_ROOT / "logs" / f"{script.stem}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        stdout=open(log_file, "w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        text=True,
    )
    log(f"Training PID={proc.pid} logs={log_file}")
    status = read_status()
    status.update(
        {
            "current_phase": f"phase2_local_training_{model}",
            "status": "in_progress",
            "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": "Hermes",
            "message": f"Training started PID={proc.pid} model={model}.",
        }
    )
    write_status(status)
    commit_and_push(["status.yaml"], f"chore: start {model} local training")
    return True


def run_benchmark_comparison() -> bool:
    script = REPO_ROOT / "benchmark_comparison.py"
    if not script.exists():
        log("benchmark_comparison.py missing")
        return False
    log("Running benchmark_comparison.py ...")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    log(f"benchmark rc={result.returncode}")
    out = (result.stdout or "") + (result.stderr or "")
    log(out[:4000])
    return result.returncode == 0


def get_latest_training_log() -> Path | None:
    logs_dir = REPO_ROOT / "logs"
    if not logs_dir.exists():
        return None
    candidates = sorted(logs_dir.glob("train_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def detect_training_completion_from_log() -> bool:
    log_path = get_latest_training_log()
    if not log_path:
        return False
    try:
        text = log_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    markers = [
        "Training complete",
        "Saved ",
        "Results saved to",
        "Epoch 50/50",
        "Epoch 100/100",
        "best.pt",
        "Training finished",
        "optimizer_step",
        "all done",
    ]
    return any(m.lower() in text.lower() for m in markers)


def handle_phase(status: dict) -> None:
    phase = str(status.get("current_phase", "")).lower().strip()
    agent = str(status.get("agent", "")).lower().strip()
    if agent not in {"", "hermes"}:
        return

    if phase in {
        "phase2_local_training",
        "phase2_local_training_yolov8",
        "phase2_local_training_yolov11",
    } and status.get("status") not in {"completed", "in_progress"}:
        log("Phase2 start requested.")
        if run_setup():
            run_training("yolov8")
        else:
            append_message("Hermes: setup_local.py zlyhal, kontroluj prosím prostredie ručne.")
    elif phase.startswith("phase2_local_training_") and status.get("status") == "in_progress":
        if detect_training_completion_from_log():
            log("Training appears complete from logs; updating status.")
            status["status"] = "completed"
            status["last_update"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            status["message"] = "Training finished based on log detection; awaiting benchmark."
            write_status(status)
            commit_and_push(["status.yaml", "messages.md"], "chore: phase2 training auto-complete")
    elif phase in {"phase3_comparison", "phase3"} and status.get("status") == "pending":
        log("Phase3 comparison requested.")
        if run_benchmark_comparison():
            status["status"] = "completed"
        else:
            status["status"] = "failed"
        status["last_update"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        status["agent"] = "Hermes"
        status["message"] = "Benchmark comparison executed."
        write_status(status)
        commit_and_push(["status.yaml", "messages.md"], "chore: benchmark comparison done")


def sync_local_yaml_if_missing() -> None:
    if not STATUS_FILE.exists():
        write_status(
            {
                "current_phase": "phase1_benchmark",
                "status": "completed",
                "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "agent": "Kilo",
                "next_phase": "phase2_local_training",
                "next_agent": "Hermes",
                "blocked_until": None,
            }
        )


def main() -> None:
    log("Watchdog starting.")
    REPO_ROOT.mkdir(parents=True, exist_ok=True)
    sync_local_yaml_if_missing()

    boot_checked_trigger = False
    last_main_sha = sh(["git", "rev-parse", "HEAD"]) or ""

    while True:
        try:
            fetch_ok = git_fetch()

            # Always watch for the trigger branch first.
            if not boot_checked_trigger and branch_exists_on_remote(TRIGGER_BRANCH):
                log(f"Trigger branch `{TRIGGER_BRANCH}` detected.")
                if switch_branch(TRIGGER_BRANCH):
                    if pull_rebase(TRIGGER_BRANCH):
                        append_message(f"Hermes: Found `{TRIGGER_BRANCH}`, switching and syncing.")
                        status = read_status()
                        status["current_phase"] = "phase2_local_training"
                        status["status"] = "pending"
                        status["last_update"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                        status["agent"] = "Hermes"
                        status["message"] = f"Switched to `{TRIGGER_BRANCH}`."
                        write_status(status)
                        commit_and_push(["status.yaml", "messages.md"], f"chore: switch to {TRIGGER_BRANCH}")
                        handle_phase(status)
                boot_checked_trigger = True

            # Also react to any main update.
            cur_main = sh(["git", "rev-parse", "ericecek/main"]) or ""
            local_sha = sh(["git", "rev-parse", "HEAD"]) or ""
            if fetch_ok and cur_main and cur_main != last_main_sha:
                log("main changed; pulling ...")
                if pull_rebase("main"):
                    log("main pulled.")
                    last_main_sha = cur_main
                    status = read_status()
                    new_sha = sh(["git", "rev-parse", "HEAD"]) or last_main_sha
                    if new_sha != local_sha:
                        handle_phase(status)

            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            log("Watchdog interrupted; exiting.")
            break
        except Exception as exc:
            log(f"Watchdog error: {exc}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
