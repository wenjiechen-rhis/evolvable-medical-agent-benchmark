from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .metrics import compute_public_metrics
from .receipt import freeze_bundle, verify_receipt
from .validation import errors_only, validate_bundle
from .io import write_json_atomic


def _bundle_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _cmd_validate(args: argparse.Namespace) -> int:
    issues = validate_bundle(args.bundle)
    for issue in issues:
        print(issue.render())
    errors = errors_only(issues)
    if errors:
        print(f"INVALID: {len(errors)} error(s), {len(issues) - len(errors)} warning(s)")
        return 1
    print(f"VALID: {len(issues)} warning(s)")
    return 0


def _cmd_freeze(args: argparse.Namespace) -> int:
    issues = validate_bundle(args.bundle, verify_frozen_receipt=False)
    errors = errors_only(issues)
    if errors:
        for issue in issues:
            print(issue.render(), file=sys.stderr)
        print("refusing to freeze an invalid execution bundle", file=sys.stderr)
        return 1
    output = args.output or args.bundle / "receipt.json"
    try:
        receipt = freeze_bundle(args.bundle, output, force=args.force)
    except Exception as exc:
        print(f"freeze failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    errors = verify_receipt(args.bundle, args.receipt)
    if errors:
        for message in errors:
            print(f"ERROR receipt: {message}")
        print(f"INVALID: {len(errors)} receipt error(s)")
        return 1
    print("VALID: frozen execution files match receipt")
    return 0


def _cmd_metrics(args: argparse.Namespace) -> int:
    issues = validate_bundle(args.bundle)
    errors = errors_only(issues)
    if errors:
        for issue in issues:
            print(issue.render(), file=sys.stderr)
        print("refusing to aggregate an invalid bundle", file=sys.stderr)
        return 1
    metrics = compute_public_metrics(args.bundle)
    if args.output:
        write_json_atomic(args.output, metrics)
    else:
        print(json.dumps(metrics, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="emab", description="Validate and report architecture-neutral formal-run bundles")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate bundle structure and protocol semantics")
    validate.add_argument("bundle", type=_bundle_path)
    validate.set_defaults(func=_cmd_validate)

    freeze = subparsers.add_parser("freeze", help="create an immutable execution receipt")
    freeze.add_argument("bundle", type=_bundle_path)
    freeze.add_argument("--output", type=_bundle_path)
    freeze.add_argument("--force", action="store_true", help="replace an existing receipt explicitly")
    freeze.set_defaults(func=_cmd_freeze)

    verify = subparsers.add_parser("verify", help="verify frozen files against a receipt")
    verify.add_argument("bundle", type=_bundle_path)
    verify.add_argument("--receipt", type=_bundle_path)
    verify.set_defaults(func=_cmd_verify)

    metrics = subparsers.add_parser("metrics", help="aggregate public metrics without scorer logic")
    metrics.add_argument("bundle", type=_bundle_path)
    metrics.add_argument("--output", type=_bundle_path)
    metrics.set_defaults(func=_cmd_metrics)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
