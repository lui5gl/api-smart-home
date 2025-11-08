"""Utility script to manage schema migrations in simple environments."""

from __future__ import annotations

import argparse
import os

from src.database.seeder import DatabaseSeeder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage database schema setup")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate tables regardless of environment",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env = os.getenv("ENV", "production").lower()

    seeder = DatabaseSeeder()

    if args.reset or env == "development":
        seeder.reset_schema()

    seeder.run_all()


if __name__ == "__main__":
    main()
