from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "dist", "build"}
PROHIBITED_PATH_PARTS = {
    "gold_answers",
    "hidden_cases",
    "reference_agent",
    "official_solution",
    "scorer.py",
}
SENSITIVE_CONTENT_TOKENS = ("rh" + "is",)


def main() -> int:
    findings: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        lowered_path = relative.lower()
        for prohibited in PROHIBITED_PATH_PARTS:
            if prohibited in lowered_path:
                findings.append(f"prohibited path pattern {prohibited!r}: {relative}")
        try:
            text = path.read_text(encoding="utf-8").lower()
        except (UnicodeDecodeError, OSError):
            continue
        for token in SENSITIVE_CONTENT_TOKENS:
            if token in text:
                findings.append(f"prohibited comparator token in {relative}")
    if findings:
        print("PUBLIC RELEASE BOUNDARY FAILED")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("PUBLIC RELEASE BOUNDARY PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
