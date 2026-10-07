"""Minimal CODEOWNERS support: the repository's own ownership data supplies RACI owners."""
from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

Rule = tuple[str, list[str]]


def parse_codeowners(text: str) -> list[Rule]:
    rules: list[Rule] = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        pattern, *owners = line.split()
        rules.append((pattern, owners))
    return rules


def load_codeowners(path: str | Path) -> list[Rule]:
    return parse_codeowners(Path(path).read_text(encoding="utf-8"))


def _matches(pattern: str, path: str) -> bool:
    path = path.lstrip("/")
    anchored = pattern.startswith("/")
    pat = pattern.lstrip("/")
    if pat.endswith("/"):  # directory rule
        return path.startswith(pat) if anchored else (path.startswith(pat) or f"/{pat}" in f"/{path}")
    if "/" not in pat:  # bare name or glob matches by basename anywhere
        return fnmatch(path.rsplit("/", 1)[-1], pat) or pat in path.split("/")
    return fnmatch(path, pat) or fnmatch(path, pat.rstrip("/") + "/*")


def owners_for(path: str, rules: list[Rule]) -> list[str]:
    """Return owners for a path. As in GitHub CODEOWNERS, the last matching rule wins."""
    result: list[str] = []
    for pattern, owners in rules:
        if _matches(pattern, path):
            result = owners
    return result
