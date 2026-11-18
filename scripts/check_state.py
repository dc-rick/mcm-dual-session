#!/usr/bin/env python3
"""Read-only consistency check for the MCM dual-session workflow.

It never writes to the project. It checks:
  - required directories and ledger headers;
  - duplicate IDs;
  - every passed task has a readable delivery JSON with the minimum fields;
  - closed issues have a close date and close evidence;
  - decided decisions have a user decision and decision date;
  - task IDs referenced from the issue ledger exist.

Usage:
  python -I check_state.py --project .
  python -I check_state.py --project . --json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

DEFAULTS = {
    "reviewer_root": "审查与规划",
    "task_dir": "审查与规划/任务单",
    "ledger_dir": "审查与规划/台账",
    "review_dir": "审查与规划/审查记录",
    "delivery_dir": "交付",
    "executor_dirs": ["code", "paper", "data", "交付"],
}

HEADERS = {
    "task": ["编号", "标题", "对应问题", "执行方", "下达日期", "前置条件",
             "状态", "任务单", "交付物", "验收日期", "验收结论"],
    "issue": ["编号", "发现日期", "严重程度", "标题", "证据", "影响", "修法",
              "验收标准", "负责方", "关联", "状态", "关闭日期", "关闭证据"],
    "decision": ["编号", "决定事项", "审查方建议", "理由", "影响到",
                 "提出日期", "状态", "用户决定", "决定日期"],
}

LEDGER_FILES = {
    "task": "任务台账.csv",
    "issue": "问题台账.csv",
    "decision": "决策台账.csv",
}

TASK_ID_RE = re.compile(r"T\d{3}(?:-R\d+)?")
DELIVERY_RE = re.compile(r"(?:交付|delivery)[\\/][^\s，,；;（(]*?_delivery\.json")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def info(self, msg: str) -> None:
        self.infos.append(msg)


def load_config(project: Path) -> dict:
    cfg = dict(DEFAULTS)
    path = project / ".dual-session" / "config.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(f"ERROR cannot read {path}: {exc}") from exc
        for key in DEFAULTS:
            if key in data:
                cfg[key] = data[key]
    return cfg


def clean_row(raw: dict) -> dict:
    out = {}
    for key, value in raw.items():
        if key is None:
            continue
        out[key.strip().lstrip("﻿")] = value.strip() if isinstance(value, str) else value
    return out


def read_ledger(path: Path, kind: str, report: Report) -> list[dict]:
    if not path.exists():
        report.error(f"missing ledger: {path}")
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = [h.strip().lstrip("﻿") for h in (reader.fieldnames or [])]
        missing = [h for h in HEADERS[kind] if h not in headers]
        if missing:
            report.error(f"{path.name}: missing columns {missing}")
        rows = [clean_row(row) for row in reader]
    if not rows:
        report.warn(f"{path.name}: no data rows")
    return rows


def unique_ids(rows: list[dict], label: str, report: Report) -> set[str]:
    seen: set[str] = set()
    for row in rows:
        item_id = (row.get("编号") or "").strip()
        if not item_id:
            report.error(f"{label}: row without 编号")
            continue
        if item_id in seen:
            report.error(f"{label}: duplicate ID {item_id}")
        seen.add(item_id)
    return seen


def is_passed(status: str) -> bool:
    s = status or ""
    return "通过" in s and not any(x in s for x in ("未通过", "出局", "取消"))


def is_closed(status: str) -> bool:
    s = (status or "").strip()
    return s.startswith("关闭") or s.startswith("已关闭") or s.startswith("部分关闭")


def is_decided(status: str) -> bool:
    return "已决定" in (status or "")


def is_skipped(status: str) -> bool:
    s = status or ""
    return any(x in s for x in ("出局", "取消"))


def find_delivery(row: dict, project: Path, cfg: dict) -> Path | None:
    task_id = (row.get("编号") or "").strip()
    text = (row.get("交付物") or "").replace("\\", "/")
    match = DELIVERY_RE.search(text)
    if match:
        candidate = project / match.group(0)
        if candidate.exists():
            return candidate
        fallback = project / cfg["delivery_dir"] / Path(match.group(0)).name
        if fallback.exists():
            return fallback
    delivery_dir = project / cfg["delivery_dir"]
    for name in (f"{task_id}_delivery.json", f"{task_id.replace('-', '')}_delivery.json"):
        candidate = delivery_dir / name
        if candidate.exists():
            return candidate
    return None


def check_delivery(path: Path, task_id: str, report: Report) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        report.error(f"{task_id}: cannot parse {path.name}: {exc}")
        return
    if not isinstance(data, dict):
        report.error(f"{task_id}: {path.name} is not a JSON object")
        return
    hard_required = ["task", "title"]
    soft_required = ["date", "status"]
    missing_hard = [key for key in hard_required if not str(data.get(key, "")).strip()]
    if missing_hard:
        report.error(f"{task_id}: {path.name} missing required fields {missing_hard}")
    missing_soft = [key for key in soft_required if not str(data.get(key, "")).strip()]
    if missing_soft:
        report.warn(f"{task_id}: {path.name} missing legacy fields {missing_soft} (pre-contract file)")
    if str(data.get("task", "")).strip() != task_id:
        report.error(f"{task_id}: delivery says task={data.get('task')!r}")
    checks = data.get("checks")
    if checks is None:
        report.warn(f"{task_id}: delivery has no checks")
    elif isinstance(checks, dict) and not checks:
        report.warn(f"{task_id}: checks is empty")
    elif not isinstance(checks, (dict, list)):
        report.error(f"{task_id}: checks must be an object or list")
    affected = data.get("affected")
    if affected is not None:
        if not isinstance(affected, list):
            report.error(f"{task_id}: affected must be a list")
        else:
            nonstandard = 0
            for index, item in enumerate(affected):
                if not isinstance(item, dict):
                    report.error(f"{task_id}: affected[{index}] is not an object")
                    continue
                if any(k not in item for k in ("location", "old", "new", "basis")):
                    nonstandard += 1
            if nonstandard:
                report.warn(
                    f"{task_id}: affected has {nonstandard}/{len(affected)} item(s) "
                    "using a pre-contract schema; expected location/old/new/basis"
                )


def check_task_ledger(rows: list[dict], project: Path, cfg: dict,
                      report: Report) -> set[str]:
    ids = unique_ids(rows, "任务台账", report)
    passed = 0
    for row in rows:
        task_id = (row.get("编号") or "").strip()
        status = (row.get("状态") or "").strip()
        if not status:
            report.error(f"{task_id}: empty 状态")
            continue
        if is_skipped(status):
            report.info(f"{task_id}: skipped ({status})")
            continue
        delivery = find_delivery(row, project, cfg)
        if is_passed(status):
            passed += 1
            if delivery is None:
                report.error(f"{task_id}: passed but no delivery JSON found")
            else:
                check_delivery(delivery, task_id, report)
                if not (row.get("验收日期") or "").strip():
                    report.warn(f"{task_id}: passed but 验收日期 is empty")
                if len((row.get("验收结论") or "").strip()) < 8:
                    report.warn(f"{task_id}: passed but 验收结论 is too short")
        elif any(x in status for x in ("已交付", "执行中", "退回", "阻塞")):
            if delivery is not None:
                check_delivery(delivery, task_id, report)
            elif "已交付" in status:
                report.warn(f"{task_id}: status says 已交付 but no delivery JSON found")
    report.info(f"tasks: {len(rows)} rows, {passed} passed, {len(ids)} unique IDs")
    return ids


def check_issue_ledger(rows: list[dict], task_ids: set[str], report: Report) -> None:
    unique_ids(rows, "问题台账", report)
    closed = 0
    open_high = 0
    for row in rows:
        issue_id = (row.get("编号") or "").strip()
        status = (row.get("状态") or "").strip()
        severity = (row.get("严重程度") or "").strip()
        if severity and severity not in ("高", "中高", "中", "低"):
            report.warn(f"{issue_id}: unknown severity {severity!r}")
        if is_closed(status):
            closed += 1
            if not (row.get("关闭日期") or "").strip():
                report.error(f"{issue_id}: closed but 关闭日期 is empty")
            if not (row.get("关闭证据") or "").strip():
                report.error(f"{issue_id}: closed but 关闭证据 is empty")
        elif severity in ("高", "中高"):
            open_high += 1
        for ref in TASK_ID_RE.findall(row.get("关联") or ""):
            if ref not in task_ids:
                report.warn(f"{issue_id}: references unknown task {ref}")
    report.info(f"issues: {len(rows)} rows, {closed} closed, {open_high} open high-severity")


def check_decision_ledger(rows: list[dict], report: Report) -> None:
    unique_ids(rows, "决策台账", report)
    decided = 0
    pending = 0
    for row in rows:
        decision_id = (row.get("编号") or "").strip()
        status = (row.get("状态") or "").strip()
        if is_decided(status):
            decided += 1
            if not (row.get("用户决定") or "").strip():
                report.error(f"{decision_id}: decided but 用户决定 is empty")
            if not (row.get("决定日期") or "").strip():
                report.error(f"{decision_id}: decided but 决定日期 is empty")
        elif "待定" in status:
            pending += 1
    report.info(f"decisions: {len(rows)} rows, {decided} decided, {pending} pending")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="project root (default: cwd)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    project = Path(args.project).resolve()
    if not project.is_dir():
        print(f"ERROR project not found: {project}")
        return 2

    cfg = load_config(project)
    report = Report()

    for key in ("reviewer_root", "task_dir", "ledger_dir", "review_dir", "delivery_dir"):
        path = project / cfg[key]
        if not path.is_dir():
            report.error(f"missing directory: {path}")

    ledger_dir = project / cfg["ledger_dir"]
    tasks = read_ledger(ledger_dir / LEDGER_FILES["task"], "task", report)
    issues = read_ledger(ledger_dir / LEDGER_FILES["issue"], "issue", report)
    decisions = read_ledger(ledger_dir / LEDGER_FILES["decision"], "decision", report)

    task_ids = check_task_ledger(tasks, project, cfg, report)
    check_issue_ledger(issues, task_ids, report)
    check_decision_ledger(decisions, report)

    if args.json:
        print(json.dumps({
            "project": str(project),
            "errors": report.errors,
            "warnings": report.warnings,
            "infos": report.infos,
        }, ensure_ascii=True, indent=2))
    else:
        print(f"Project: {project}")
        for line in report.infos:
            print(f"INFO  {line}")
        for line in report.warnings:
            print(f"WARN  {line}")
        for line in report.errors:
            print(f"ERROR {line}")
        print(f"\nSummary: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")

    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
