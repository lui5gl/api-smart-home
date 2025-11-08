"""Business logic for database seed operations."""

from ..database import Database, DatabaseSeeder


class SeedService:
    """Public interface for triggering seeding routines."""

    def __init__(self, database: Database | None = None) -> None:
        self._seeder = DatabaseSeeder(database)

    def seed_database(self) -> dict[str, str]:
        return self._seeder.run_all()
