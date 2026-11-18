# MCM Dual-Session

**A two-session reviewer/executor protocol for MCM/ICM paper production.**

Two long-lived Claude Code sessions work on the same paper repository without sharing a chat context:

- **Reviewer / planner** owns `审查与规划/` — task orders, review records, and three CSV ledgers (task, issue, decision).
- **Executor** owns `code/`, `paper/`, `data/runs/T00x/`, and `交付/`.

They coordinate only through files: a task order with numbered acceptance checks, a delivery JSON with evidence, and a ledger row that records the verdict. The point is not "two agents"; it is **independent review plus recoverable state**.

This skill was extracted from the 2026 CQU-C MCM paper workspace: [dc-rick/mcm-2026-cqu-problemc](https://github.com/dc-rick/mcm-2026-cqu-problemc).

---

## What it enforces

| Boundary | Reviewer | Executor |
|---|---|---|
| `审查与规划/` | write | read-only |
| `code/`, `paper/`, `data/`, `交付/` | read-only | write |
| existing `data/` inputs | read-only | read-only; new outputs go to `data/runs/T00x/` |

Hard rules:

- The reviewer never edits code, paper, data, or delivery files — not even a typo. It writes a task instead.
- The executor never edits the ledgers or any file under `审查与规划/`. Status changes are proposed in the delivery `notes`; the reviewer records them.
- A task can pass only when every acceptance check has evidence that the reviewer can re-run or recompute.
- Every number in the paper must trace to a result file produced by the current run, not to memory or an old draft.

---

## Repository layout

```text
SKILL.md                    entry point: roles, boundaries, loop, contracts
references/protocol.md      full protocol: lifecycle, acceptance, ledgers, recovery
references/templates.md     task-order HTML, delivery JSON, review record, CSV headers
scripts/check_state.py      read-only consistency check for ledgers and deliveries
```

---

## Install

Project-level:

```bash
mkdir -p <project>/.claude/skills
cp -R . <project>/.claude/skills/mcm-dual-session
```

Global:

```bash
cp -R . ~/.claude/skills/mcm-dual-session
```

Claude Code scans skills at session start. In the current session, read `SKILL.md` by path.

---

## Quick start

In the reviewer session:

```text
使用 mcm-dual-session。这个会话是指导方（审查/规划/验收）。
项目根：<path>。先读三本台账和最近一次交付，报告当前状态与下一步。
```

In the executor session:

```text
使用 mcm-dual-session。这个会话是执行方（代码/论文/数据/交付）。
项目根：<path>。先读任务台账，报告所有“待执行/执行中/退回”的任务，不要开始写。
```

If the project does not have the directories yet, `SKILL.md` §10 and `references/templates.md` §7 give the scaffold and CSV headers.

---

## Check state

```bash
python -I scripts/check_state.py --project <project>
```

It checks ledger headers, duplicate IDs, whether passed tasks have a readable delivery JSON, whether closed issues have close evidence, and whether decided decisions have a user decision. It never writes to the project.

Exit codes: `0` no errors (warnings allowed), `1` errors, `2` project not found.

---

## When not to use

- A one-off question or a single typo: one session is faster.
- Exploratory work with no acceptance criteria: define what "done" means first.
- A hotfix: fix first, but if a paper number changes, still write a delivery and a review record.

---

## License

No license has been chosen for this repository. If you want others to reuse it, add one (MIT is a common choice for skills).
