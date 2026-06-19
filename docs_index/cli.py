from __future__ import annotations

import argparse
from typing import Sequence

from docs_index.reconcile import apply_updates
from docs_index.reconcile import reconcile_tree
from docs_index.paths import resolve_root
from docs_index.watch import watch_root


def _add_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default="docs", help="docs root directory")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="doc-ledger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fix_parser = subparsers.add_parser("fix", help="fix doc-ledger issues")
    _add_root_argument(fix_parser)
    fix_parser.set_defaults(command="fix")

    check_parser = subparsers.add_parser("check", help="check doc-ledger issues")
    _add_root_argument(check_parser)
    check_parser.set_defaults(command="check")

    watch_parser = subparsers.add_parser("watch", help="watch doc-ledger changes")
    _add_root_argument(watch_parser)
    watch_parser.add_argument("--once", action="store_true", help="run once and exit")
    watch_parser.set_defaults(command="watch")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command in {"fix", "check"}:
        try:
            root = resolve_root(args.root)
            if not root.exists():
                parser.error(f"docs root does not exist: {root}")

            result = reconcile_tree(root)
        except SystemExit:
            raise
        except Exception as exc:  # pragma: no cover - defensive CLI boundary
            parser.exit(2, f"doc-ledger error: {exc}\n")

        if args.command == "fix":
            changed = apply_updates(result)
            print(f"doc-ledger fix updated {changed} file(s)")
            if result.messages:
                print(f"doc-ledger fix reconciliation messages: {len(result.messages)}")
            return 0

        if result.updates:
            print("doc-ledger check failed")
            for update in result.updates:
                print(str(update.path))
            return 1

        print("doc-ledger check passed")
        return 0
    elif args.command == "watch":
        try:
            root = resolve_root(args.root)
            if not root.exists():
                parser.error(f"docs root does not exist: {root}")

            return watch_root(root, once=args.once)
        except SystemExit:
            raise
        except Exception as exc:  # pragma: no cover - defensive CLI boundary
            parser.exit(2, f"doc-ledger error: {exc}\n")

    return 0
