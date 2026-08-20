"""Validate the repository invariants required by the documentation CI."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
WORKFLOW = ROOT / "00-project" / "development-workflow.md"


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)


def check_code_fences() -> list[str]:
    errors: list[str] = []
    fence = re.compile(r"^\s*(```|~~~)")
    for path in markdown_files():
        count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if fence.match(line))
        if count % 2:
            errors.append(f"{path.relative_to(ROOT)}: unbalanced code fences")
    return errors


def check_local_links() -> list[str]:
    errors: list[str] = []
    link = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for path in markdown_files():
        for target in link.findall(path.read_text(encoding="utf-8")):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:") or target.startswith("#"):
                continue
            target_path = (path.parent / target).resolve()
            try:
                target_path.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not target_path.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing link target {target}")
    return errors


def check_baseline_entry() -> list[str]:
    errors: list[str] = []
    readme = README.read_text(encoding="utf-8")
    for target in (
        "./01-product/mvp-module-plan.md",
        "./04-database/data-dictionary.md",
        "./00-project/project-directory-guide.md",
    ):
        if target not in readme or not (ROOT / target.removeprefix("./")).exists():
            errors.append(f"README.md: baseline link missing or invalid: {target}")
    if "Markdown 是可编辑主版本来源" not in readme:
        errors.append("README.md: Markdown primary-source statement is missing")
    return errors


def check_workflow_invariants() -> list[str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    errors: list[str] = []
    if "M1～M5" not in text:
        errors.append("development-workflow.md: current M1～M5 baseline is missing")
    if "LinkForty" not in text or "API" not in text:
        errors.append("development-workflow.md: LinkForty API boundary is missing")
    if "Alembic" not in text:
        errors.append("development-workflow.md: Alembic migration rule is missing")
    if "BLOCKER" not in text or "MAJOR" not in text:
        errors.append("development-workflow.md: review severity gates are missing")
    return errors


def main() -> int:
    errors = check_code_fences() + check_local_links() + check_baseline_entry() + check_workflow_invariants()
    if errors:
        print("Documentation validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Documentation validation passed ({len(markdown_files())} Markdown files checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
