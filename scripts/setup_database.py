"""
Database Setup and Data Insertion Script

This script:
1. Creates the PostgreSQL database (if it doesn't exist)
2. Creates the schema (banks and reviews tables)
3. Inserts bank data
4. Inserts review data with proper foreign key mapping
5. Validates data integrity

Usage:
    python scripts/setup_database.py
"""

import sys
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'bank_reviews',
    'user': 'postgres',
    'password': '0000',
    'port': '5432'
}

# Bank name to app name mapping
BANK_APP_MAPPING = {
    'Commercial Bank of Ethiopia': 'Mobile Banking App',
    'Bank of Abyssinia': 'Mobile Banking App',
    'Dashen Bank': 'Amole App'
}


def create_database():
    """
    Create the database if it doesn't exist.
    Connects to the default 'postgres' database first.
    """
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            database='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(DB_CONFIG['database'])
                )
            )
            print(f"✅ Created database: {DB_CONFIG['database']}")
        else:
            print(f"✅ Database {DB_CONFIG['database']} already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise


def get_connection():
    """Establish connection to the bank_reviews database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        raise


def create_schema(conn):
    """Create database schema by executing schema.sql."""
    try:
        cursor = conn.cursor()
        
        # Read and execute schema file
        schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema SQL
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Database schema created successfully")
        cursor.close()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating schema: {e}")
        raise


def insert_banks(conn):
    """
    Insert bank data into the banks table.
    Returns a dictionary mapping bank_name to bank_id.
    """
    try:
        cursor = conn.cursor()
        
        # Get unique banks from the data
        bank_names = list(BANK_APP_MAPPING.keys())
        
        bank_id_map = {}
        
        for bank_name in bank_names:
            app_name = BANK_APP_MAPPING[bank_name]
            
            # Check if bank already exists
            cursor.execute(
                "SELECT bank_id FROM banks WHERE bank_name = %s",
                (bank_name,)
            )
            existing = cursor.fetchone()
            
            if existing:
                bank_id_map[bank_name] = existing[0]
                print(f"  ✓ Bank already exists: {bank_name} (ID: {existing[0]})")
            else:
                # Insert new bank
                cursor.execute(
                    """
                    INSERT INTO banks (bank_name, app_name)
                    VALUES (%s, %s)
                    RETURNING bank_id
                    """,
                    (bank_name, app_name)
                )
                bank_id = cursor.fetchone()[0]
                bank_id_map[bank_name] = bank_id
                print(f"  ✓ Inserted bank: {bank_name} (ID: {bank_id})")
        
        conn.commit()
        cursor.close()
        
        print(f"✅ Inserted {len(bank_id_map)} banks")
        return bank_id_map
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting banks: {e}")
        raise


def load_review_data():
    """
    Load review data from processed CSV and merge with date information.
    Returns a DataFrame with all required columns.
    """
    print("\n📂 Loading review data...")
    
    # Load processed sentiment analysis results
    processed_path = Path(__file__).parent.parent / 'data' / 'processed' / 'sentiment_analysis_results.csv'
    
    if not processed_path.exists():
        raise FileNotFoundError(f"Processed data not found: {processed_path}")
    
    df = pd.read_csv(processed_path)
    print(f"  ✓ Loaded {len(df)} reviews from processed data")
    
    # Try to load original cleaned data for dates
    cleaned_path = Path(__file__).parent.parent / 'data' / 'cleaned' / 'clean_reviews.csv'
    
    if cleaned_path.exists():
        print("  ✓ Found original cleaned data, merging dates...")
        df_cleaned = pd.read_csv(cleaned_path)
        
        # Merge on review_text and bank_name to get dates
        # Use a combination of review_text and bank_name for matching
        df_cleaned['merge_key'] = (
            df_cleaned['review_text'].str[:100] + '|' + df_cleaned['bank']
        )
        df['merge_key'] = (
            df['review_text'].str[:100] + '|' + df['bank_name']
        )
        
        # Merge to get dates
        df = df.merge(
            df_cleaned[['merge_key', 'date']],
            on='merge_key',
            how='left'
        )
        
        # Convert date to timestamp
        df['review_date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.drop(['merge_key', 'date'], axis=1, errors='ignore')
        
        merged_count = df['review_date'].notna().sum()
        print(f"  ✓ Merged dates for {merged_count} reviews")
        
        # For reviews without dates, use a reasonable default
        missing_dates = df['review_date'].isna().sum()
        if missing_dates > 0:
            default_date = datetime.now()
            df['review_date'] = df['review_date'].fillna(default_date)
            print(f"  ⚠ Set default date for {missing_dates} reviews without dates")
    else:
        print("  ⚠ Original cleaned data not found, using default timestamp for dates")
        # Use current timestamp if date not available
        df['review_date'] = datetime.now()
    
    # Ensure source column exists
    if 'source' not in df.columns:
        df['source'] = 'Google Play'
    
    # Select and rename columns for database insertion
    df_db = pd.DataFrame({
        'bank_name': df['bank_name'],
        'review_text': df['review_text'],
        'rating': df['rating'],
        'review_date': df['review_date'],
        'sentiment_label': df['sentiment_label'],
        'sentiment_score': df['sentiment_score'],
        'source': df['source']
    })
    
    # Remove rows with missing critical data
    initial_count = len(df_db)
    df_db = df_db.dropna(subset=['bank_name', 'review_text', 'rating'])
    removed = initial_count - len(df_db)
    
    if removed > 0:
        print(f"  ⚠ Removed {removed} rows with missing critical data")
    
    print(f"  ✅ Prepared {len(df_db)} reviews for insertion")
    
    return df_db


def insert_reviews(conn, df, bank_id_map):
    """
    Insert review data into the reviews table.
    Uses parameterized queries for safety.
    """
    try:
        cursor = conn.cursor()
        
        inserted_count = 0
        skipped_count = 0
        
        # Prepare insert statement with parameterized query
        insert_query = """
        INSERT INTO reviews (
            bank_id, review_text, rating, review_date,
            sentiment_label, sentiment_score, source
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for _, row in df.iterrows():
            bank_name = row['bank_name']
            
            # Get bank_id from mapping
            bank_id = bank_id_map.get(bank_name)
            
            if not bank_id:
                skipped_count += 1
                print(f"  ⚠ Skipping review: Bank '{bank_name}' not found in banks table")
                continue
            
            # Prepare values
            values = (
                bank_id,
                str(row['review_text']) if pd.notna(row['review_text']) else None,
                int(row['rating']) if pd.notna(row['rating']) else None,
                row['review_date'] if pd.notna(row['review_date']) else None,
                str(row['sentiment_label']) if pd.notna(row['sentiment_label']) else None,
                float(row['sentiment_score']) if pd.notna(row['sentiment_score']) else None,
                str(row['source']) if pd.notna(row['source']) else None
            )
            
            try:
                cursor.execute(insert_query, values)
                inserted_count += 1
                
                # Commit in batches of 100 for better performance
                if inserted_count % 100 == 0:
                    conn.commit()
                    print(f"  ✓ Inserted {inserted_count} reviews...")
                    
            except Exception as e:
                print(f"  ⚠ Error inserting review: {e}")
                skipped_count += 1
                continue
        
        # Final commit
        conn.commit()
        cursor.close()
        
        print(f"✅ Inserted {inserted_count} reviews")
        if skipped_count > 0:
            print(f"⚠ Skipped {skipped_count} reviews")
        
        return inserted_count
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error inserting reviews: {e}")
        raise


def validate_data(conn):
    """
    Validate data integrity and return summary statistics.
    """
    try:
        cursor = conn.cursor()
        
        print("\n" + "="*60)
        print("📊 DATA VALIDATION")
        print("="*60)
        
        # Total reviews per bank
        print("\n1. Total Reviews per Bank:")
        cursor.execute("""
            SELECT b.bank_name, COUNT(r.review_id) as review_count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_id, b.bank_name
            ORDER BY review_count DESC
        """)
        
        reviews_per_bank = cursor.fetchall()
        for bank_name, count in reviews_per_bank:
            print(f"   {bank_name}: {count} reviews")
        
        # Average rating per bank
        print("\n2. Average Rating per Bank:")
        cursor.execute("""
            SELECT b.bank_name, 
                   ROUND(AVG(r.rating)::numeric, 2) as avg_rating,
                   COUNT(r.review_id) as review_count
            FROM banks b
            LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_id, b.bank_name
            ORDER BY avg_rating DESC
        """)
        
        avg_ratings = cursor.fetchall()
        for bank_name, avg_rating, count in avg_ratings:
            print(f"   {bank_name}: {avg_rating} (from {count} reviews)")
        
        # Foreign key constraint verification
        print("\n3. Foreign Key Constraint Verification:")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM reviews r
            WHERE r.bank_id NOT IN (SELECT bank_id FROM banks)
        """)
        orphaned_reviews = cursor.fetchone()[0]
        
        if orphaned_reviews == 0:
            print("   ✅ All reviews have valid bank_id references")
        else:
            print(f"   ❌ Found {orphaned_reviews} reviews with invalid bank_id")
        
        # Null value check
        print("\n4. Null Value Analysis:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviews,
                COUNT(review_text) as reviews_with_text,
                COUNT(rating) as reviews_with_rating,
                COUNT(sentiment_label) as reviews_with_sentiment,
                COUNT(review_date) as reviews_with_date
            FROM reviews
        """)
        
        null_stats = cursor.fetchone()
        total, with_text, with_rating, with_sentiment, with_date = null_stats
        
        print(f"   Total reviews: {total}")
        print(f"   Reviews with text: {with_text} ({with_text/total*100:.1f}%)")
        print(f"   Reviews with rating: {with_rating} ({with_rating/total*100:.1f}%)")
        print(f"   Reviews with sentiment: {with_sentiment} ({with_sentiment/total*100:.1f}%)")
        print(f"   Reviews with date: {with_date} ({with_date/total*100:.1f}%)")
        
        # Total count verification
        print("\n5. Total Count Verification:")
        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]
        print(f"   Total reviews in database: {total_reviews}")
        
        if total_reviews >= 400:
            print(f"   ✅ Meets requirement of 400+ reviews")
        else:
            print(f"   ⚠ Below requirement of 400+ reviews")
        
        cursor.close()
        
        return {
            'total_reviews': total,
            'reviews_per_bank': dict(reviews_per_bank),
            'avg_ratings': {name: float(avg) for name, avg, _ in avg_ratings},
            'orphaned_reviews': orphaned_reviews,
            'null_stats': {
                'with_text': with_text,
                'with_rating': with_rating,
                'with_sentiment': with_sentiment,
                'with_date': with_date
            }
        }
        
    except Exception as e:
        print(f"❌ Error validating data: {e}")
        raise


def main():
    """Main execution function."""
    print("="*60)
    print("DATABASE SETUP AND DATA INSERTION")
    print("="*60)
    print()
    
    try:
        # Step 1: Create database
        print("STEP 1: Creating database...")
        create_database()
        
        # Step 2: Connect to database
        print("\nSTEP 2: Connecting to database...")
        conn = get_connection()
        print("✅ Connected to database")
        
        # Step 3: Create schema
        print("\nSTEP 3: Creating database schema...")
        create_schema(conn)
        
        # Step 4: Insert banks
        print("\nSTEP 4: Inserting bank data...")
        bank_id_map = insert_banks(conn)
        
        # Step 5: Load review data
        print("\nSTEP 5: Loading review data...")
        df_reviews = load_review_data()
        
        # Step 6: Insert reviews
        print("\nSTEP 6: Inserting review data...")
        inserted_count = insert_reviews(conn, df_reviews, bank_id_map)
        
        # Step 7: Validate data
        print("\nSTEP 7: Validating data...")
        validation_results = validate_data(conn)
        
        # Close connection
        conn.close()
        
        # Final summary
        print("\n" + "="*60)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  • Banks inserted: {len(bank_id_map)}")
        print(f"  • Reviews inserted: {inserted_count}")
        print(f"  • Total reviews in database: {validation_results['total_reviews']}")
        print(f"\n✅ All data successfully stored in PostgreSQL!")
        
        return validation_results
        
    except Exception as e:
        print(f"\n❌ Error during database setup: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()

