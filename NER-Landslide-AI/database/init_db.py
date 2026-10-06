from __future__ import annotations

from sqlalchemy import create_engine, text

from backend.app.config import SETTINGS
from backend.app.models import Base


def ensure_database_exists() -> None:
    admin_url = SETTINGS.database_url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_engine(admin_url, future=True)

    with admin_engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
            {"database_name": SETTINGS.postgres_db},
        ).scalar()
        if result is None:
            connection.execute(text(f'CREATE DATABASE "{SETTINGS.postgres_db}"'))


def initialize_database() -> None:
    ensure_database_exists()
    engine = create_engine(SETTINGS.database_url, future=True)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {SETTINGS.postgres_db}")
