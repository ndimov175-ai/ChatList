"""
Database manager for ChatList application.
Handles database connection, migrations, and basic operations.
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from contextlib import contextmanager

from chatlist.config.settings import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and migrations."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file. If None, uses config default.
        """
        self.db_path = Path(db_path) if db_path else config.database_path
        self.migrations_dir = Path(__file__).parent.parent / 'migrations'
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create database file if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            logger.info(f"Creating new database at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """
        Get database connection context manager.

        Usage:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def execute(self, query: str, params: Optional[Tuple] = None):
        """
        Execute a single query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount

    def execute_many(self, query: str, params_list: List[Tuple]):
        """
        Execute a query multiple times with different parameters.

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[sqlite3.Row]:
        """
        Fetch a single row.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Row object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[sqlite3.Row]:
        """
        Fetch all rows.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of Row objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def _get_migration_files(self) -> List[Path]:
        """Get sorted list of migration SQL files."""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []

        migration_files = sorted(
            self.migrations_dir.glob("*.sql"),
            key=lambda x: int(x.stem.split('_')[0]) if x.stem.split('_')[0].isdigit() else 0
        )
        return migration_files

    def _get_applied_migrations(self) -> List[str]:
        """Get list of already applied migration filenames."""
        # Create migrations tracking table if it doesn't exist
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename VARCHAR(255) NOT NULL UNIQUE,
                    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

        rows = self.fetch_all("SELECT filename FROM migrations ORDER BY id")
        return [row['filename'] for row in rows]

    def run_migrations(self) -> int:
        """
        Run all pending migrations.

        Returns:
            Number of migrations applied
        """
        migration_files = self._get_migration_files()
        applied_migrations = self._get_applied_migrations()
        applied_count = 0

        for migration_file in migration_files:
            filename = migration_file.name
            if filename in applied_migrations:
                logger.debug(f"Migration {filename} already applied, skipping")
                continue

            logger.info(f"Applying migration: {filename}")
            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()

                with self.get_connection() as conn:
                    # Execute migration in a transaction
                    conn.executescript(migration_sql)
                    # Record migration as applied
                    conn.execute(
                        "INSERT INTO migrations (filename) VALUES (?)",
                        (filename,)
                    )

                applied_count += 1
                logger.info(f"Successfully applied migration: {filename}")
            except Exception as e:
                logger.error(f"Error applying migration {filename}: {e}")
                raise

        if applied_count == 0:
            logger.info("No pending migrations")
        else:
            logger.info(f"Applied {applied_count} migration(s)")

        return applied_count

    def initialize_database(self):
        """Initialize database by running all migrations."""
        logger.info("Initializing database...")
        self.run_migrations()
        logger.info("Database initialization complete")


# Global database manager instance
db_manager = DatabaseManager()

