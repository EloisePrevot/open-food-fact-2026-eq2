"""Chargement: charge les données vers SQLite, MongoDB et Qdrant."""

from __future__ import annotations

from argparse import ArgumentParser

from elt.config import Settings
from elt.connections import DatabaseConnections


def open_load_connections(settings: Settings | None = None) -> DatabaseConnections:
    """Ouvre les moteurs cibles du chargement, sans écrire de données."""
    return DatabaseConnections.connect(settings or Settings.from_environment())


def verify_database_connections(settings: Settings | None = None) -> None:
    """Vérifie SQLite, MongoDB et Qdrant par une opération sans effet de bord."""
    with open_load_connections(settings) as connections:
        connections.verify_connections()


def main() -> None:
    parser = ArgumentParser(description="Commandes du pipeline ELT Open Food Facts Québec.")
    parser.add_argument(
        "--check-connections",
        action="store_true",
        help="vérifie les connexions SQLite, MongoDB et Qdrant",
    )
    arguments = parser.parse_args()

    if arguments.check_connections:
        verify_database_connections()
        print("SQLite, MongoDB and Qdrant connections are available.")
        return

    parser.error("Specify --check-connections. Data loading is not implemented yet.")


if __name__ == "__main__":
    main()
