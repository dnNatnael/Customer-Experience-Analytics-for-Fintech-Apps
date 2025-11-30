"""
Database Validation Script

This script runs validation queries to verify data integrity and generate
a summary report of the database contents.

Usage:
    python scripts/validate_database.py
"""

import sys
import os
from pathlib import Path
import psycopg2
from datetime import datetime
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


def get_connection():
    """Establish connection to the bank_reviews database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Database 'bank_reviews' exists")
        print("  3. Connection credentials are correct")
        raise


def run_validation_queries(conn):
    """Run validation queries and return results."""
    cursor = conn.cursor()
    results = {}
    
    print("="*60)
    print("DATABASE VALIDATION REPORT")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Total reviews per bank
    print("1. TOTAL REVIEWS PER BANK")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            b.bank_name,
            COUNT(r.review_id) AS total_reviews
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_id, b.bank_name
        ORDER BY total_reviews DESC
    """)
    
    reviews_per_bank = cursor.fetchall()
    results['reviews_per_bank'] = {}
    for bank_name, count in reviews_per_bank:
        print(f"   {bank_name}: {count} reviews")
        results['reviews_per_bank'][bank_name] = count
    
    # 2. Average rating per bank
    print("\n2. AVERAGE RATING PER BANK")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            b.bank_name,
            ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
            COUNT(r.review_id) AS review_count
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_id, b.bank_name
        ORDER BY avg_rating DESC
    """)
    
    avg_ratings = cursor.fetchall()
    results['avg_ratings'] = {}
    for bank_name, avg_rating, count in avg_ratings:
        if avg_rating:
            print(f"   {bank_name}: {avg_rating} (from {count} reviews)")
            results['avg_ratings'][bank_name] = float(avg_rating)
        else:
            print(f"   {bank_name}: No reviews")
    
    # 3. Foreign key constraint verification
    print("\n3. FOREIGN KEY CONSTRAINT VERIFICATION")
    print("-" * 60)
    cursor.execute("""
        SELECT COUNT(*) 
        FROM reviews r
        WHERE r.bank_id NOT IN (SELECT bank_id FROM banks)
    """)
    orphaned_reviews = cursor.fetchone()[0]
    
    if orphaned_reviews == 0:
        print("   ✅ All reviews have valid bank_id references")
        results['fk_valid'] = True
    else:
        print(f"   ❌ Found {orphaned_reviews} reviews with invalid bank_id")
        results['fk_valid'] = False
    
    # 4. Null value analysis
    print("\n4. NULL VALUE ANALYSIS")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_reviews,
            COUNT(review_text) AS reviews_with_text,
            COUNT(rating) AS reviews_with_rating,
            COUNT(sentiment_label) AS reviews_with_sentiment,
            COUNT(sentiment_score) AS reviews_with_sentiment_score,
            COUNT(review_date) AS reviews_with_date,
            COUNT(source) AS reviews_with_source
        FROM reviews
    """)
    
    null_stats = cursor.fetchone()
    total, with_text, with_rating, with_sentiment, with_score, with_date, with_source = null_stats
    
    print(f"   Total reviews: {total}")
    print(f"   Reviews with text: {with_text} ({with_text/total*100:.1f}%)")
    print(f"   Reviews with rating: {with_rating} ({with_rating/total*100:.1f}%)")
    print(f"   Reviews with sentiment label: {with_sentiment} ({with_sentiment/total*100:.1f}%)")
    print(f"   Reviews with sentiment score: {with_score} ({with_score/total*100:.1f}%)")
    print(f"   Reviews with date: {with_date} ({with_date/total*100:.1f}%)")
    print(f"   Reviews with source: {with_source} ({with_source/total*100:.1f}%)")
    
    results['null_stats'] = {
        'total': total,
        'with_text': with_text,
        'with_rating': with_rating,
        'with_sentiment': with_sentiment,
        'with_score': with_score,
        'with_date': with_date,
        'with_source': with_source
    }
    
    # 5. Rating distribution
    print("\n5. RATING DISTRIBUTION")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            rating,
            COUNT(*) AS count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) AS percentage
        FROM reviews
        WHERE rating IS NOT NULL
        GROUP BY rating
        ORDER BY rating DESC
    """)
    
    rating_dist = cursor.fetchall()
    results['rating_distribution'] = {}
    for rating, count, pct in rating_dist:
        print(f"   {rating} stars: {count} reviews ({pct}%)")
        results['rating_distribution'][rating] = count
    
    # 6. Sentiment distribution
    print("\n6. SENTIMENT DISTRIBUTION")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            sentiment_label,
            COUNT(*) AS count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM reviews), 2) AS percentage
        FROM reviews
        WHERE sentiment_label IS NOT NULL
        GROUP BY sentiment_label
        ORDER BY count DESC
    """)
    
    sentiment_dist = cursor.fetchall()
    results['sentiment_distribution'] = {}
    for label, count, pct in sentiment_dist:
        print(f"   {label}: {count} reviews ({pct}%)")
        results['sentiment_distribution'][label] = count
    
    # 7. Total count verification
    print("\n7. TOTAL COUNT VERIFICATION")
    print("-" * 60)
    cursor.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cursor.fetchone()[0]
    print(f"   Total reviews in database: {total_reviews}")
    
    if total_reviews >= 400:
        print(f"   ✅ Meets requirement of 400+ reviews")
        results['meets_requirement'] = True
    else:
        print(f"   ⚠ Below requirement of 400+ reviews")
        results['meets_requirement'] = False
    
    results['total_reviews'] = total_reviews
    
    # 8. Data range check
    print("\n8. DATA RANGE CHECK")
    print("-" * 60)
    cursor.execute("""
        SELECT 
            MIN(review_date) AS earliest_date,
            MAX(review_date) AS latest_date,
            COUNT(*) AS reviews_with_dates
        FROM reviews
        WHERE review_date IS NOT NULL
    """)
    
    date_range = cursor.fetchone()
    if date_range[0]:
        print(f"   Earliest review: {date_range[0]}")
        print(f"   Latest review: {date_range[1]}")
        print(f"   Reviews with dates: {date_range[2]}")
        results['date_range'] = {
            'earliest': str(date_range[0]),
            'latest': str(date_range[1]),
            'count': date_range[2]
        }
    else:
        print("   ⚠ No dates available in reviews")
        results['date_range'] = None
    
    cursor.close()
    
    return results


def generate_summary_report(results):
    """Generate a summary report from validation results."""
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    print(f"\n✅ Total Reviews: {results['total_reviews']}")
    print(f"✅ Requirement Met (400+): {'Yes' if results['meets_requirement'] else 'No'}")
    print(f"✅ Foreign Keys Valid: {'Yes' if results['fk_valid'] else 'No'}")
    
    print("\n📊 Reviews per Bank:")
    for bank, count in results['reviews_per_bank'].items():
        print(f"   • {bank}: {count}")
    
    print("\n⭐ Average Ratings:")
    for bank, avg_rating in results['avg_ratings'].items():
        print(f"   • {bank}: {avg_rating}")
    
    print("\n" + "="*60)
    print("✅ VALIDATION COMPLETE")
    print("="*60)
    
    return results


def main():
    """Main execution function."""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = get_connection()
        print("✅ Connected to database\n")
        
        # Run validation queries
        results = run_validation_queries(conn)
        
        # Generate summary
        generate_summary_report(results)
        
        # Close connection
        conn.close()
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()

