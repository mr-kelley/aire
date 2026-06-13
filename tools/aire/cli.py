"""aire CLI entry point and subcommand dispatch.

Governing spec: specs/tools/aire/architecture-spec.md (Invocation Contract).
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .doctor import run_doctor


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

    parser.error(f"unknown command: {args.command}")  # exits 2
    return 2  # unreachable; keeps type checkers happy


def console_main() -> None:
    sys.exit(main())
