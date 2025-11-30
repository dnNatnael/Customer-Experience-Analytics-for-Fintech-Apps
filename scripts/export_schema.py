"""
Database Schema Export Script

Exports the database schema to a SQL file for backup and documentation.

Usage:
    python scripts/export_schema.py
"""

import sys
import os
from pathlib import Path
import subprocess
import warnings
warnings.filterwarnings('ignore')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'bank_reviews',
    'user': 'postgres',
    'password': '0000',
    'port': '5432'
}


def export_schema():
    """Export database schema to SQL file."""
    try:
        # Create database directory if it doesn't exist
        db_dir = Path(__file__).parent.parent / 'database'
        db_dir.mkdir(exist_ok=True)
        
        output_file = db_dir / 'exported_schema.sql'
        
        # Build pg_dump command
        cmd = [
            'pg_dump',
            '-U', DB_CONFIG['user'],
            '-d', DB_CONFIG['database'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '--schema-only',
            '--no-owner',
            '--no-privileges',
            '-f', str(output_file)
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_CONFIG['password']
        
        print("Exporting database schema...")
        print(f"Command: {' '.join(cmd)}")
        
        # Run pg_dump
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Schema exported successfully to: {output_file}")
            print(f"📁 File size: {output_file.stat().st_size / 1024:.2f} KB")
            return True
        else:
            print(f"❌ Error exporting schema:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Error: pg_dump not found")
        print("Please ensure PostgreSQL client tools are installed and in PATH")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def export_full_database():
    """Export full database (schema + data) to SQL file."""
    try:
        db_dir = Path(__file__).parent.parent / 'database'
        db_dir.mkdir(exist_ok=True)
        
        output_file = db_dir / 'bank_reviews_full_dump.sql'
        
        cmd = [
            'pg_dump',
            '-U', DB_CONFIG['user'],
            '-d', DB_CONFIG['database'],
            '-h', DB_CONFIG['host'],
            '-p', DB_CONFIG['port'],
            '--no-owner',
            '--no-privileges',
            '-f', str(output_file)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_CONFIG['password']
        
        print("Exporting full database...")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Full database exported to: {output_file}")
            print(f"📁 File size: {output_file.stat().st_size / 1024:.2f} KB")
            return True
        else:
            print(f"❌ Error exporting database:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ Error: pg_dump not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main execution function."""
    print("="*60)
    print("DATABASE SCHEMA EXPORT")
    print("="*60)
    print()
    
    # Export schema only
    success = export_schema()
    
    if success:
        print("\n" + "="*60)
        print("✅ EXPORT COMPLETE")
        print("="*60)
        
        # Ask if user wants full export
        print("\nWould you like to export the full database (schema + data)?")
        print("Run: python scripts/export_schema.py --full")
    else:
        print("\n" + "="*60)
        print("❌ EXPORT FAILED")
        print("="*60)
        print("\nPlease ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. pg_dump is in your PATH")
        print("  3. Database 'bank_reviews' exists")
        print("  4. Connection credentials are correct")


if __name__ == "__main__":
    import sys
    if '--full' in sys.argv:
        export_full_database()
    else:
        main()

