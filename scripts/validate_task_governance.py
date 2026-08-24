"""Validate task IDs, Epic/Issue governance and intentional V1.4 boundaries."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "00-project" / "development-task-checklist.md"
MASTER = ROOT / "00-project" / "master-checklist.md"
TASK_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
EPIC_IDS = {
    "EPIC-CHARTER-001",
    "EPIC-P0-001",
    "EPIC-P1-001",
    "EPIC-API-001",
    "EPIC-API-002",
    "EPIC-DATA-001",
    "EPIC-SEC-001",
    "EPIC-SCHEMA-001",
    "EPIC-REF-001",
    "EPIC-A-M2-001",
    "EPIC-A-M4-001",
    "EPIC-B-M3-001",
    "EPIC-B-M5-001",
    "EPIC-IMP-001",
    "EPIC-X-IMP-001",
    "EPIC-EXP-001",
    "EPIC-X-EXP-001",
    "EPIC-FRONTEND-001",
    "EPIC-RELEASE-001",
    "EPIC-M2-001",
    "EPIC-M4-001",
}
ALLOWED_ISSUES = {"#7", "#9", "#10"}
DEFERRED_PREFIXES = ("P0-CAS-", "DEC-CAS-", "P0-NFC-", "DEC-NFC-")


def table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| ID |"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 18 and TASK_ID_RE.fullmatch(cells[0]):
            rows.append(cells)
    return rows


def governance_rows(text: str) -> list[list[str]]:
    match = re.search(r"^## Epic/Issue/任务索引\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return []
    rows: list[list[str]] = []
    for line in match.group(1).splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| Epic ID"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if all(set(cell) <= {"-", " "} for cell in cells):
            continue
        if len(cells) == 7:
            rows.append(cells)
    return rows


def check_tasks(task_text: str, errors: list[str]) -> tuple[set[str], set[str]]:
    rows = table_rows(task_text)
    if not rows:
        errors.append("development-task-checklist.md: no task rows found")
        return set(), set()
    ids = [row[0] for row in rows]
    duplicates = sorted({task_id for task_id in ids if ids.count(task_id) > 1})
    if duplicates:
        errors.append(f"duplicate task IDs: {', '.join(duplicates)}")
    task_ids = set(ids)
    epic_refs: set[str] = set()
    for row in rows:
        task_id, status, owner, dependencies, output, acceptance, version = (
            row[0], row[6], row[8], row[10], row[11], row[12], row[15]
        )
        epic_refs.update(re.findall(r"EPIC-[A-Z0-9-]+", dependencies))
        if status == "阻塞待确认" and any(not value or value == "待产生" for value in (owner, dependencies, output, acceptance)):
            errors.append(f"{task_id}: blocker must have owner, dependencies, output and acceptance")
        if task_id.startswith(DEFERRED_PREFIXES):
            if status != "延期" or "V1.4" not in version:
                errors.append(f"{task_id}: Casdoor/NFC root task must remain 延期 / V1.4")
        dependency_tokens = [token.strip().strip("`") for token in dependencies.split(",") if token.strip()]
        for dependency in dependency_tokens:
            if dependency.startswith("EPIC-"):
                if dependency not in EPIC_IDS:
                    errors.append(f"{task_id}: unknown Epic dependency {dependency}")
                continue
            if dependency not in task_ids and not dependency.startswith("ENV-"):
                errors.append(f"{task_id}: unknown dependency {dependency}")
    if "同 Key" not in task_text or "已知缺陷" not in task_text:
        errors.append("development-task-checklist.md: LinkForty same-key known defect must remain explicit")
    return task_ids, epic_refs


def check_index(master_text: str, task_ids: set[str], epic_refs: set[str], errors: list[str]) -> None:
    rows = governance_rows(master_text)
    if len(rows) != len(EPIC_IDS):
        errors.append(f"master-checklist.md: expected {len(EPIC_IDS)} Epic index rows, found {len(rows)}")
    indexed = {row[0] for row in rows}
    if indexed != EPIC_IDS:
        errors.append(f"master-checklist.md: Epic index mismatch; missing={sorted(EPIC_IDS-indexed)}, extra={sorted(indexed-EPIC_IDS)}")
    for row in rows:
        epic, issue, task_range, owner, dependencies, acceptance, version = row
        if not re.search(r"#(?:7|9|10)", issue):
            errors.append(f"{epic}: Issue must be #7, #9 or #10")
        if any(not value for value in (task_range, owner, dependencies, acceptance, version)):
            errors.append(f"{epic}: index fields cannot be empty")
        for task_id in re.findall(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b", task_range):
            if task_id.startswith("EPIC-"):
                continue
            if task_id not in task_ids and not task_id.endswith("~006") and not task_id.endswith("~002"):
                errors.append(f"{epic}: index references unknown task {task_id}")
    for epic in epic_refs:
        if epic not in indexed:
            errors.append(f"{epic}: referenced by task list but missing from Epic index")
    if "#7" not in master_text or "#9" not in master_text or "#10" not in master_text:
        errors.append("master-checklist.md: existing Issue #7/#9/#10 mapping is incomplete")
    if not re.search(r"#9[^\n]*P0-CAS-001.*DEC-CAS-001", master_text):
        errors.append("master-checklist.md: Casdoor deferred task range is not mapped to Issue #9")
    if not re.search(r"#10[^\n]*P0-NFC-001.*DEC-NFC-001", master_text):
        errors.append("master-checklist.md: NFC deferred task range is not mapped to Issue #10")
    if re.search(r"Issue\s+#(?!7\b|9\b|10\b)\d+", master_text):
        errors.append("master-checklist.md: governance index references an unapproved Issue")


def main() -> int:
    errors: list[str] = []
    task_text = TASKS.read_text(encoding="utf-8")
    master_text = MASTER.read_text(encoding="utf-8")
    task_ids, epic_refs = check_tasks(task_text, errors)
    check_index(master_text, task_ids, epic_refs, errors)
    if errors:
        print("Task governance validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Task governance validation passed ({len(task_ids)} tasks, {len(EPIC_IDS)} Epics, Issues #7/#9/#10).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
