"""Passerelle pour le module load."""

from __future__ import annotations

import sys
from pathlib import Path

# Remonte d'un cran pour atteindre la racine 'elt' et trouver main.py
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from main import main

if __name__ == "__main__":
    main()