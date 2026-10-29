"""Chargement Open Food Facts filtré à l'Amérique du Nord, sans table de transit.

Open Food Facts exporte un TSV d'environ 4,5 millions de produits (~13 Go). Le
disque du conteneur PostgreSQL ne peut pas accueillir une copie complète du
fichier en table de transit. On filtre donc AVANT le chargement : on lit le TSV
ligne par ligne sur l'hôte (opération peu coûteuse : un simple test sur la
colonne ``countries_tags``) et on ne pousse vers PostgreSQL, via
``COPY ... FROM STDIN``, que les produits ``en:canada``, ``en:united-states`` ou
``en:mexico``.

Aucune ligne non nord-américaine n'est écrite dans la base : seule la table
finale ``off_products`` existe, et elle reste petite.
"""

from __future__ import annotations

import csv
import sys
from collections.abc import Iterator
from pathlib import Path

import psycopg
from psycopg import sql

# Certains champs OFF (listes d'ingrédients, tags) dépassent la limite par défaut
# de 128 Kio du module csv. On relève la limite au maximum supporté par la plateforme.
def _raise_csv_field_size_limit() -> None:
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 2


_raise_csv_field_size_limit()

FINAL_TABLE = "off_products"

# Tags de pays conservés (Amérique du Nord), comparés comme des tokens entiers.
NORTH_AMERICAN_COUNTRY_TAGS = frozenset({"en:canada", "en:united-states", "en:mexico"})

_COUNTRIES_TAGS_COLUMN = "countries_tags"

# Fréquence d'affichage de la progression (une ligne tous les N enregistrements
# LUS). On n'imprime pas à chaque ligne : avec ~4,5 M de lignes, cela ralentirait
# le chargement. Un intervalle élevé rend le coût d'affichage négligeable.
_PROGRESS_INTERVAL = 250_000

# Taille des blocs lus pour compter les lignes du fichier (comptage d'octets rapide).
_LINE_COUNT_CHUNK_SIZE = 1 << 20  # 1 Mio


def read_off_header(csv_path: Path) -> list[str]:
    """Lit la première ligne du TSV et retourne les noms de colonnes assainis."""
    with csv_path.open("r", encoding="utf-8", newline="") as source_file:
        header = next(csv.reader(source_file, delimiter="\t"))

    return [_sanitize_column_name(name) for name in header]


def _sanitize_column_name(name: str) -> str:
    """Rend un nom de colonne OFF valide et stable pour PostgreSQL."""
    sanitized = name.strip().lower()
    return sanitized.replace("-", "_").replace(".", "_").replace(" ", "_")


def load_off_north_america(connection: psycopg.Connection, csv_path: Path) -> int:
    """Charge uniquement les produits nord-américains de off.csv dans PostgreSQL.

    Retourne le nombre de produits conservés.
    """
    columns = read_off_header(csv_path)
    if _COUNTRIES_TAGS_COLUMN not in columns:
        raise ValueError(
            f"Colonne '{_COUNTRIES_TAGS_COLUMN}' absente de l'en-tête de {csv_path.name}"
        )

    countries_index = columns.index(_COUNTRIES_TAGS_COLUMN)
    total_rows = _count_data_rows(csv_path)
    _recreate_final_table(connection, columns)
    kept_count = _copy_north_american_rows(
        connection, csv_path, columns, countries_index, total_rows
    )
    connection.commit()

    return kept_count


def _count_data_rows(csv_path: Path) -> int:
    """Compte rapidement les lignes de données (hors en-tête) pour le pourcentage.

    Comptage d'octets (nombre de sauts de ligne), approximatif si des champs
    contiennent des retours à la ligne, mais suffisant pour une barre de progression.
    """
    newline_count = 0
    with csv_path.open("rb") as source_file:
        while chunk := source_file.read(_LINE_COUNT_CHUNK_SIZE):
            newline_count += chunk.count(b"\n")

    return max(newline_count - 1, 0)  # retire la ligne d'en-tête


def _recreate_final_table(connection: psycopg.Connection, columns: list[str]) -> None:
    column_definitions = sql.SQL(", ").join(
        sql.SQL("{} TEXT").format(sql.Identifier(column)) for column in columns
    )
    connection.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(FINAL_TABLE)))
    connection.execute(
        sql.SQL("CREATE UNLOGGED TABLE {} ({})").format(
            sql.Identifier(FINAL_TABLE), column_definitions
        )
    )
    connection.commit()


def _copy_north_american_rows(
    connection: psycopg.Connection,
    csv_path: Path,
    columns: list[str],
    countries_index: int,
    total_rows: int,
) -> int:
    """Pousse via COPY FROM STDIN les seules lignes nord-américaines."""
    copy_statement = sql.SQL("COPY {} ({}) FROM STDIN").format(
        sql.Identifier(FINAL_TABLE),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )

    kept_count = 0
    with connection.cursor() as cursor, cursor.copy(copy_statement) as copy:
        for row in _iter_north_american_rows(csv_path, columns, countries_index, total_rows):
            copy.write_row(row)
            kept_count += 1

    return kept_count


def _report_progress(scanned_count: int, kept_count: int, total_rows: int) -> None:
    if total_rows > 0:
        percentage = min(scanned_count / total_rows * 100, 100.0)
        print(
            f"  {percentage:5.1f}% — scanned {scanned_count:,}/{total_rows:,} rows, "
            f"kept {kept_count:,} North American products"
        )
    else:
        print(f"  scanned {scanned_count:,} rows, kept {kept_count:,} North American products")


def _iter_north_american_rows(
    csv_path: Path, columns: list[str], countries_index: int, total_rows: int
) -> Iterator[list[str | None]]:
    """Lit le TSV et ne retourne que les lignes dont les pays sont nord-américains."""
    expected_field_count = len(columns)
    scanned_count = 0
    kept_count = 0

    with csv_path.open("r", encoding="utf-8", newline="") as source_file:
        reader = csv.reader(source_file, delimiter="\t")
        next(reader)  # saute l'en-tête

        for fields in reader:
            scanned_count += 1
            if scanned_count % _PROGRESS_INTERVAL == 0:
                _report_progress(scanned_count, kept_count, total_rows)

            # Les lignes mal formées (nombre de colonnes inattendu) sont ignorées.
            if len(fields) != expected_field_count:
                continue

            if _is_north_american(fields[countries_index]):
                kept_count += 1
                # Les champs vides deviennent NULL en base.
                yield [field if field != "" else None for field in fields]

    _report_progress(scanned_count, kept_count, total_rows)


def _is_north_american(countries_tags: str) -> bool:
    """Vrai si l'un des tags de pays (séparés par des virgules) est nord-américain."""
    tags = countries_tags.split(",")
    return any(tag.strip() in NORTH_AMERICAN_COUNTRY_TAGS for tag in tags)
