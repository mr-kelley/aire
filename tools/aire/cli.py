"""aire CLI entry point and subcommand dispatch.

Governing spec: specs/tools/aire/architecture-spec.md (Invocation Contract).
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .audit import run_audit
from .doctor import run_doctor
from .history import HistoryError, record as history_record
from .history_report import run_report as history_report
from .map import run_map


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aire", description="Aire governance tooling (deterministic, no network)"
    )
    parser.add_argument(
        "--version", action="version", version=f"aire {__version__}"
    )
    sub = parser.add_subparsers(dest="command", metavar="<subcommand>")

    doctor = sub.add_parser(
        "doctor", help="validate repository and environment (read-only)"
    )
    doctor.add_argument("--json", action="store_true", help="emit JSON")

    mp = sub.add_parser("map", help="spec coverage mapping")
    msub = mp.add_subparsers(dest="map_command", metavar="<action>")
    msub.add_parser("check", help="verify coverage (gate; exit 1 on findings)")
    mrep = msub.add_parser("report", help="emit the coverage map")
    mrep.add_argument("--json", action="store_true", help="emit JSON")

    aud = sub.add_parser("audit", help="governance liveness audit (mechanical checks)")
    aud.add_argument("--json", action="store_true", help="emit JSON")

    history = sub.add_parser("history", help="promotion records")
    hsub = history.add_subparsers(dest="history_command", metavar="<action>")
    rec = hsub.add_parser("record", help="write a promote/<slug> tag")
    rec.add_argument("--slug", help="record slug (default: inferred from branch)")
    rec.add_argument("--commit", default="HEAD", help="commit to tag (default: HEAD)")
    rec.add_argument("--tests-sha", dest="tests_sha", help="commit the tests ran against")
    rec.add_argument("--tests-command", dest="tests_command", help="how tests were invoked")
    rec.add_argument("--tests-outcome", dest="tests_outcome", default="PASS",
                     choices=["PASS", "N/A"], help="test outcome (default: PASS)")
    rec.add_argument("--spec", dest="specs", action="append", help="governing spec (repeatable)")
    rec.add_argument("--sprint", help="governing sprint file")
    rec.add_argument("--decision", dest="decisions", action="append",
                     help="decision ID touched (repeatable)")
    rec.add_argument("--note", dest="notes", help="optional one-liner")
    rec.add_argument("--dry-run", action="store_true", help="preview; create nothing")

    rep = hsub.add_parser("report", help="render the audited project history")
    rep.add_argument("--detail", action="store_true", help="per-promotion detail view")
    rep.add_argument("--chain", metavar="SLUG", help="audit chain for one promotion")
    rep.add_argument("--ref", default="main", help="ref to analyze (default: main)")
    rep.add_argument("--json", action="store_true", help="emit JSON")

    return parser


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)  # exits 0 on --version, 2 on parse error

    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "doctor":
        return run_doctor(as_json=args.json)
    if args.command == "map":
        if args.map_command is None:
            print("usage: aire map {check|report}", file=sys.stderr)
            return 2
        if args.map_command == "check":
            return run_map("check")
        if args.map_command == "report":
            return run_map("report", as_json=args.json)
    if args.command == "audit":
        return run_audit(as_json=args.json)
    if args.command == "history":
        if args.history_command is None:
            print("usage: aire history record [options]", file=sys.stderr)
            return 2
        if args.history_command == "record":
            try:
                return history_record(
                    slug=args.slug, commit=args.commit, tests_sha=args.tests_sha,
                    tests_command=args.tests_command, tests_outcome=args.tests_outcome,
                    specs=args.specs, sprint=args.sprint, decisions=args.decisions,
                    notes=args.notes, dry_run=args.dry_run,
                )
            except HistoryError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
        if args.history_command == "report":
            view = "chain" if args.chain else "detail" if args.detail else "summary"
            try:
                return history_report(
                    view=view, slug=args.chain, ref=args.ref, as_json=args.json,
                )
            except HistoryError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2

    parser.error(f"unknown command: {args.command}")  # exits 2
    return 2  # unreachable; keeps type checkers happy


def console_main() -> None:
    sys.exit(main())
