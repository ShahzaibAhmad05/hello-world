#!/usr/bin/env python3
"""
Database migration script for Task Management System
Handles initial setup and migrations
"""

import sqlite3
import os
from pathlib import Path


def get_db_path():
    """Get database path"""
    backend_dir = Path(__file__).parent.parent / 'backend'
    return backend_dir / 'task_manager.db'


def run_migration(cursor, migration_file):
    """Run a single migration file"""
    print(f"Running migration: {migration_file}")
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    # Execute SQL statements
    cursor.executescript(sql)
    print(f"✓ Migration completed: {migration_file}")


def init_database():
    """Initialize database with schema and seed data"""
    db_path = get_db_path()
    db_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if database exists
    db_exists = os.path.exists(db_path)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        if not db_exists:
            print("Creating new database...")
            
            # Run schema migration
            schema_file = os.path.join(db_dir, 'schema.sql')
            if os.path.exists(schema_file):
                run_migration(cursor, schema_file)
            
            # Ask if user wants seed data
            response = input("\nWould you like to add seed data for testing? (y/n): ")
            if response.lower() == 'y':
                seed_file = os.path.join(db_dir, 'seed_data.sql')
                if os.path.exists(seed_file):
                    run_migration(cursor, seed_file)
                    print("\n✓ Database initialized with seed data")
                    print("\nTest accounts created:")
                    print("  Username: john_doe   | Password: password123")
                    print("  Username: jane_smith | Password: password123")
                    print("  Username: test_user  | Password: password123")
            else:
                print("\n✓ Database initialized without seed data")
        else:
            print("Database already exists. No changes made.")
            print("To reset the database, delete the file and run this script again.")
        
        conn.commit()
        
    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()


def main():
    """Main entry point"""
    print("=" * 60)
    print("Task Management System - Database Migration")
    print("=" * 60)
    
    init_database()
    
    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
