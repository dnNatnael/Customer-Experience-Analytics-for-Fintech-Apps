"""
Database Connection Module

Provides functions for connecting to the PostgreSQL database.
"""

import psycopg2
from psycopg2 import pool
import os
from typing import Optional


# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'bank_reviews'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '0000'),
    'port': os.getenv('DB_PORT', '5432')
}


def create_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Create a connection to the PostgreSQL database.
    
    Returns:
        psycopg2 connection object if successful, None otherwise
    """
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to the PostgreSQL database")
        return connection
    except psycopg2.OperationalError as e:
        print(f"❌ Error connecting to database: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Database 'bank_reviews' exists")
        print("  3. Connection credentials are correct")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_connection() -> bool:
    """
    Test the database connection.
    
    Returns:
        True if connection is successful, False otherwise
    """
    conn = create_connection()
    if conn:
        conn.close()
        return True
    return False


if __name__ == "__main__":
    connection = create_connection()
    if connection:
        connection.close()
        print("Connection test successful!")