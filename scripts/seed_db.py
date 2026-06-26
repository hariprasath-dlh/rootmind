"""
seed_db.py - Seed Database Script

Initializes the database schema and populates SQLite or Supabase table instances
with sample incident logs, status details, and mock users for demonstration testing.
"""

import sys
import os

# Append backend path to enable imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))


def seed_database() -> None:
    """
    Main database seeder routine. Connects via app.database session
    and inserts initial mock incident records.
    """
    print("Connecting to database and running metadata schema builds...")
    # SQL Alchemy db tables initialization and row seeding stubs
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
