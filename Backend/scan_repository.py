from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .scanner import scan_repository
except ImportError:
    from scanner import scan_repository


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a local repository and output discovered files as JSON."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Local repository path to scan. Defaults to current directory.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )

    args = parser.parse_args()
    result = scan_repository(Path(args.path))

    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent))


if __name__ == "__main__":
    main()