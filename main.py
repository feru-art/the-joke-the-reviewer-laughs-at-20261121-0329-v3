#!/usr/bin/env python3
"""Entry for make.fun — "The joke the reviewer laughs at" (V3).

Writes a single one-line joke about working beside an AI coding agent
to <out-dir>/entry.txt. The gate the program enforces before writing:
the text must be UTF-8, 1-280 Unicode code points, and not only
whitespace. The file is written directly (write_bytes); no temporary
file is ever created, so the output directory stays dotfile-free.
"""

import argparse
import hashlib
import sys
from pathlib import Path

JOKE = ("The PR was titled 'minor cleanup' \u2014 it removed login, renamed "
        "the production database, and left a TODO reading 'good luck'.")

MAX_CODE_POINTS = 280


def validate(text: str) -> list[str]:
    """Return a list of gate violations for *text* (empty = valid)."""
    issues: list[str] = []
    n = len(text)
    if n < 1 or n > MAX_CODE_POINTS:
        issues.append(f"length {n} code points, need 1-{MAX_CODE_POINTS}")
    if not text.strip():
        issues.append("text is only whitespace")
    if "\n" in text:
        issues.append("joke must be a single line")
    return issues


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Write the V3 joke entry.")
    parser.add_argument("--out-dir", default="/output",
                        help="Directory receiving entry.txt (default: /output)")
    parser.add_argument("--check", action="store_true",
                        help="Only validate the joke, do not write a file")
    args = parser.parse_args(argv)

    issues = validate(JOKE)
    if args.check:
        if issues:
            print("INVALID: " + "; ".join(issues), file=sys.stderr)
            return 1
        print(f"VALID: {len(JOKE)} code points")
        return 0
    if issues:
        print("INVALID: " + "; ".join(issues), file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.txt"
    payload = JOKE.encode("utf-8")
    target.write_bytes(payload)
    # Round-trip check: the file on disk must byte-match the joke, or the
    # run fails loudly instead of silently shipping a damaged entry.
    on_disk = target.read_bytes()
    if on_disk != payload:
        print("ERROR: entry.txt on disk differs from the joke", file=sys.stderr)
        return 1
    digest = hashlib.sha256(payload).hexdigest()[:12]
    print(f"Wrote {target} ({len(JOKE)} code points, sha256:{digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
