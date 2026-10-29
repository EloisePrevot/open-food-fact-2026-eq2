"""Affichage de la progression en pourcentage pour les commandes longues.

Deux stratégies :

* ``ByteProgress`` suit l'avancement par rapport à la taille d'un fichier en
  octets (utile pour l'export OFF de 13 Go dont le nombre de lignes est inconnu
  avant lecture) ;
* ``CountProgress`` suit l'avancement par rapport à un nombre total connu
  d'éléments (utile pour le chargement MongoDB dont le total vient de PostgreSQL).
"""

from __future__ import annotations

import sys
import time


class _Printer:
    def __init__(self, label: str, min_interval_seconds: float = 0.5) -> None:
        self._label = label
        self._min_interval = min_interval_seconds
        self._last_emit = 0.0
        self._last_percent = -1
        # Sur un terminal, on réécrit la même ligne avec « \r ». Hors terminal
        # (journaux Docker, redirections), « \r » reste invisible tant qu'aucune
        # fin de ligne n'arrive : on émet alors des lignes complètes throttlées.
        self._is_tty = sys.stdout.isatty()

    def _emit(self, percent: int, suffix: str, force: bool = False) -> None:
        now = time.monotonic()
        changed = percent != self._last_percent
        due = now - self._last_emit >= self._min_interval
        if not force and (not changed or not due):
            return
        self._last_emit = now
        self._last_percent = percent
        line = f"  {self._label} : {percent:3d}% {suffix}"
        if self._is_tty:
            sys.stdout.write(f"\r{line}")
        else:
            sys.stdout.write(f"{line}\n")
        sys.stdout.flush()

    def _finish(self, suffix: str) -> None:
        self._emit(100, suffix, force=True)
        if self._is_tty:
            sys.stdout.write("\n")
            sys.stdout.flush()


class ByteProgress(_Printer):
    """Progression basée sur le nombre d'octets lus d'un fichier de taille connue."""

    def __init__(self, label: str, total_bytes: int) -> None:
        super().__init__(label)
        self._total = max(total_bytes, 1)

    def update(self, bytes_read: int, items: int) -> None:
        percent = min(int(bytes_read * 100 / self._total), 99)
        self._emit(percent, f"({items:,} enregistrements)")

    def done(self, items: int) -> None:
        self._finish(f"({items:,} enregistrements)")


class CountProgress(_Printer):
    """Progression basée sur un nombre total d'éléments connu à l'avance."""

    def __init__(self, label: str, total_items: int) -> None:
        super().__init__(label)
        self._total = max(total_items, 1)

    def update(self, items: int) -> None:
        percent = min(int(items * 100 / self._total), 99)
        self._emit(percent, f"({items:,}/{self._total:,})")

    def done(self, items: int) -> None:
        self._finish(f"({items:,}/{self._total:,})")
