#!/usr/bin/env python3
"""Deprecated: use update_audio.sh instead (keeps absolute paths in the shell script)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    script = ROOT / "update_audio.sh"
    print("import_sources.py is deprecated; running update_audio.sh ...")
    subprocess.run(["bash", str(script)], check=True)


if __name__ == "__main__":
    main()
