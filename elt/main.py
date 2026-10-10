"""Orchestrateur principal du projet elt."""

from __future__ import annotations

import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def main() -> None:
    from load.load import main as load_main
    load_main()

if __name__ == "__main__":
    main()