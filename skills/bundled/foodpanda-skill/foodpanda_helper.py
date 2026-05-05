#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compatibility shim.

Use `scripts/foodpanda_helper.py` as the canonical entrypoint.
This file is kept for backward compatibility.
"""

from pathlib import Path
import runpy
import sys

TARGET = Path(__file__).resolve().parent / "scripts" / "foodpanda_helper.py"
if not TARGET.exists():
    raise SystemExit(f"Missing entry script: {TARGET}")

sys.path.insert(0, str(TARGET.parent))
runpy.run_path(str(TARGET), run_name="__main__")
