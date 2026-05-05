#!/usr/bin/env python3
"""Compatibility wrapper for the minimal skill validation gate.

The validation core now lives in format_check.py so format_check.py and
quick_validate.py cannot drift on overlapping frontmatter rules.
"""

from __future__ import annotations

import sys

from format_check import validate_skill


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        return 1

    valid, message = validate_skill(sys.argv[1])
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
