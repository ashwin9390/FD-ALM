"""Command line: fd-alm check | triage | metrics."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .codeowners import load_codeowners
from .gatekeeper import check, has_errors
from .metrics import load_samples, summarize
from .registry import RegistryError, load_registry
from .triage import load_changes, triage


def _cmd_check(args: argparse.Namespace) -> int:
    entries = load_registry(args.registry)
    rules = load_codeowners(args.codeowners) if args.codeowners else None
    findings = check(entries, rules, max_idle_days=args.max_idle_days)
    for finding in findings:
        print(finding)
    errors = sum(1 for f in findings if f.severity == "error")
    print(f"{len(entries)} entries checked: {errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if has_errors(findings) else 0


def _cmd_triage(args: argparse.Namespace) -> int:
    entries = load_registry(args.registry)
    queue = triage(load_changes(args.changes), entries)
    for item in queue:
        c = item.change
        print(f"{item.quadrant} {item.lane:<16} {c.id}  {c.title}  ({item.reason}, {c.lines_changed} lines)")
    return 0


def _cmd_metrics(args: argparse.Namespace) -> int:
    summary = summarize(load_samples(args.samples))
    for key, value in summary.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fd-alm", description="Framework-Driven Agent Lifecycle Management")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="run gatekeeper policies on a registry file")
    p_check.add_argument("registry")
    p_check.add_argument("--codeowners", help="path to a CODEOWNERS file")
    p_check.add_argument("--max-idle-days", type=int, default=90)
    p_check.set_defaults(func=_cmd_check)

    p_triage = sub.add_parser("triage", help="order agent-authored changes for human review")
    p_triage.add_argument("registry")
    p_triage.add_argument("changes")
    p_triage.set_defaults(func=_cmd_triage)

    p_metrics = sub.add_parser("metrics", help="summarize AI-era cycle time from a CSV (ai_s,queue_s,review_s)")
    p_metrics.add_argument("samples")
    p_metrics.set_defaults(func=_cmd_metrics)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (RegistryError, FileNotFoundError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
