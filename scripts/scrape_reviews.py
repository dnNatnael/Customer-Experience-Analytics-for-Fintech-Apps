"""
Task 1: Data Collection and Preprocessing
Scrapes Google Play Store reviews for Ethiopian banking apps
and creates a clean, structured dataset.
"""

import pandas as pd
import numpy as np
from google_play_scraper import app, reviews, Sort
from datetime import datetime
from tqdm import tqdm
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
BANK_APPS = {
    'CBE': {
        'name': 'Commercial Bank of Ethiopia',
        'app_id': 'com.combanketh.mobilebanking'
    },
    'BOA': {
        'name': 'Bank of Abyssinia',
        'app_id': 'com.boa.boaMobileBanking'
    },
    'Dashen': {
        'name': 'Dashen Bank',
        'app_id': 'com.cr2.amolelight'
    }
}

REVIEWS_PER_BANK = 500  # Scrape more to account for duplicates
LANG = 'en'
SORT = Sort.NEWEST


def scrape_reviews_for_app(app_id: str, app_name: str, count: int = REVIEWS_PER_BANK, lang: str = LANG, sort: Sort = SORT):
    """
    Scrape reviews for a specific app from Google Play Store.
    
    Args:
        app_id: Google Play Store app ID
        app_name: Display name of the app/bank
        count: Number of reviews to scrape (default: 400)
        lang: Language code (default: 'en')
        sort: Sort order (default: Sort.NEWEST)
    
    Returns:
        List of review dictionaries
    """
    print(f"\n{'='*60}")
    print(f"Scraping reviews for: {app_name}")
    print(f"App ID: {app_id}")
    print(f"Target: {count} reviews")
    print(f"{'='*60}")
    
    reviews_data = []
    continuation_token = None
    target_count = count
    
    # Use a batch approach to collect reviews
    batch_size = 200  # google-play-scraper typically returns up to 200 per call
    
    try:
        with tqdm(total=target_count, desc=f"Scraping {app_name}") as pbar:
            while len(reviews_data) < target_count:
                # Calculate how many more we need
                remaining = target_count - len(reviews_data)
                batch_count = min(batch_size, remaining)
                
                try:
                    # Scrape reviews
                    result, continuation_token = reviews(
                        app_id,
                        lang=lang,
                        country='us',  # Using 'us' for English reviews
                        sort=sort,
                        count=batch_count,
                        continuation_token=continuation_token
                    )
                    
                    # Add reviews to our list
                    reviews_data.extend(result)
                    pbar.update(len(result))
                    
                    # If no more reviews available, break
                    if continuation_token is None or len(result) == 0:
                        print(f"\n⚠️  Only {len(reviews_data)} reviews available for {app_name}")
                        break
                        
                    # Small delay to avoid rate limiting
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"\n❌ Error scraping reviews: {str(e)}")
                    break
        
        print(f"✅ Successfully scraped {len(reviews_data)} reviews for {app_name}")
        return reviews_data
        
    except Exception as e:
        print(f"\n❌ Failed to scrape reviews for {app_name}: {str(e)}")
        return []


def preprocess_reviews(reviews_list: list, bank_name: str):
    """
    Clean and preprocess scraped reviews.
    
    Args:
        reviews_list: List of review dictionaries
        bank_name: Name of the bank
    
    Returns:
        DataFrame with cleaned reviews
    """
    if not reviews_list:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(reviews_list)
    
    # Select and rename relevant columns
    processed_df = pd.DataFrame({
        'review_text': df['content'].astype(str),
        'rating': df['score'].astype(int),
        'date': pd.to_datetime(df['at']).dt.date,
        'bank': bank_name,
        'source': 'Google Play'
    })
    
    # Remove duplicates based on review_text
    initial_count = len(processed_df)
    processed_df = processed_df.drop_duplicates(subset=['review_text'], keep='first')
    duplicates_removed = initial_count - len(processed_df)
    
    if duplicates_removed > 0:
        print(f"  Removed {duplicates_removed} duplicate review(s)")
    
    # Drop records with missing review text or rating
    before_clean = len(processed_df)
    processed_df = processed_df.dropna(subset=['review_text', 'rating'])
    
    # Remove reviews with empty or whitespace-only text
    processed_df = processed_df[processed_df['review_text'].str.strip() != '']
    processed_df = processed_df[processed_df['review_text'] != 'nan']
    
    after_clean = len(processed_df)
    removed_missing = before_clean - after_clean
    
    if removed_missing > 0:
        print(f"  Removed {removed_missing} review(s) with missing/invalid data")
    
    # Standardize dates to YYYY-MM-DD format
    processed_df['date'] = pd.to_datetime(processed_df['date']).dt.strftime('%Y-%m-%d')
    
    # Reset index
    processed_df = processed_df.reset_index(drop=True)
    
    return processed_df


def scrape_all_reviews():
    """
    Main function to scrape reviews for all three banking apps
    and create a cleaned dataset.
    """
    print("\n" + "="*60)
    print("TASK 1: Data Collection and Preprocessing")
    print("Ethiopian Banking Apps - Google Play Store Reviews")
    print("="*60)
    
    all_reviews_df = []
    
    # Scrape reviews for each bank
    for bank_code, bank_info in BANK_APPS.items():
        app_id = bank_info['app_id']
        app_name = bank_info['name']
        
        # Scrape reviews
        raw_reviews = scrape_reviews_for_app(app_id, app_name, REVIEWS_PER_BANK)
        
        if raw_reviews:
            # Preprocess reviews
            print(f"\n📝 Preprocessing reviews for {app_name}...")
            cleaned_df = preprocess_reviews(raw_reviews, app_name)
            
            if not cleaned_df.empty:
                all_reviews_df.append(cleaned_df)
                print(f"✅ Processed {len(cleaned_df)} clean reviews for {app_name}")
            else:
                print(f"⚠️  No clean reviews after preprocessing for {app_name}")
        else:
            print(f"⚠️  No reviews scraped for {app_name}")
    
    # Combine all reviews
    if all_reviews_df:
        # Separate Dashen Bank reviews from others for priority handling
        dashen_df = None
        other_banks_df = []
        
        for df in all_reviews_df:
            bank_name = df['bank'].iloc[0] if len(df) > 0 else None
            if bank_name == 'Dashen Bank':
                dashen_df = df
            else:
                other_banks_df.append(df)
        
        # Combine other banks first
        if other_banks_df:
            final_df = pd.concat(other_banks_df, ignore_index=True)
        else:
            final_df = pd.DataFrame()
        
        # Handle Dashen Bank with priority strategy
        if dashen_df is not None and len(dashen_df) > 0:
            # Remove duplicates within Dashen reviews
            dashen_initial = len(dashen_df)
            dashen_df = dashen_df.drop_duplicates(subset=['review_text'], keep='first')
            dashen_dups = dashen_initial - len(dashen_df)
            if dashen_dups > 0:
                print(f"  Removed {dashen_dups} duplicate review(s) within Dashen Bank")
            
            if not final_df.empty:
                # Remove duplicates from other banks that match Dashen reviews
                # This ensures Dashen reviews are prioritized when duplicates exist across banks
                dashen_texts_lower = set(dashen_df['review_text'].str.lower())
                before_other = len(final_df)
                final_df = final_df[~final_df['review_text'].str.lower().isin(dashen_texts_lower)]
                removed_from_other = before_other - len(final_df)
                if removed_from_other > 0:
                    print(f"  Removed {removed_from_other} duplicate review(s) from other banks that match Dashen reviews")
            
            # Combine Dashen with other banks
            final_df = pd.concat([final_df, dashen_df], ignore_index=True)
        
        # Final cleanup: remove any remaining duplicates (should be minimal)
        initial_total = len(final_df)
        final_df = final_df.drop_duplicates(subset=['review_text'], keep='first')
        final_duplicates = initial_total - len(final_df)
        
        if final_duplicates > 0:
            print(f"\n📊 Removed {final_duplicates} additional duplicate review(s) across all banks")
        
        # Ensure date format consistency
        final_df['date'] = pd.to_datetime(final_df['date']).dt.strftime('%Y-%m-%d')
        
        # Save to CSV
        output_path = os.path.join('data', 'cleaned', 'clean_reviews.csv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        final_df.to_csv(output_path, index=False, encoding='utf-8')
        
        # Print summary statistics
        print("\n" + "="*60)
        print("📊 FINAL DATASET SUMMARY")
        print("="*60)
        print(f"Total reviews: {len(final_df)}")
        print(f"\nReviews by bank:")
        print(final_df['bank'].value_counts().to_string())
        print(f"\nReviews by rating:")
        print(final_df['rating'].value_counts().sort_index().to_string())
        print(f"\nDate range: {final_df['date'].min()} to {final_df['date'].max()}")
        print(f"\n✅ Dataset saved to: {output_path}")
        print("="*60)
        
        # Check KPIs
        print("\n📈 KPI CHECK:")
        total_reviews = len(final_df)
        reviews_per_bank = final_df['bank'].value_counts()
        
        print(f"✓ Total reviews: {total_reviews} (Target: 1,200+)")
        print(f"✓ Reviews per bank:")
        for bank in BANK_APPS.values():
            count = reviews_per_bank.get(bank['name'], 0)
            status = "✓" if count >= 400 else "✗"
            print(f"  {status} {bank['name']}: {count} (Target: 400+)")
        
        missing_data_pct = (final_df.isnull().sum().sum() / (len(final_df) * len(final_df.columns))) * 100
        print(f"✓ Missing data: {missing_data_pct:.2f}% (Target: <5%)")
        
        return final_df
    else:
        print("\n❌ No reviews were successfully scraped and processed.")
        return pd.DataFrame()


def verify_dataset(csv_path='data/cleaned/clean_reviews.csv'):
    """
    Verify the cleaned dataset meets all requirements.
    
    Args:
        csv_path: Path to the CSV file to verify
    """
    print('\n=== DATASET VERIFICATION ===\n')
    
    # Check file exists
    file_exists = os.path.exists(csv_path)
    print(f'✓ File exists: {file_exists}')
    
    if not file_exists:
        print('❌ Dataset file not found!')
        return False
    
    # Load dataset
    df = pd.read_csv(csv_path)
    
    # Basic stats
    print(f'\n✓ Total reviews: {len(df)}')
    print(f'✓ Columns: {list(df.columns)}')
    print(f'✓ Missing data: {df.isnull().sum().sum()} cells')
    print(f'✓ File size: {os.path.getsize(csv_path) / 1024:.2f} KB')
    
    # Verify structure
    required_columns = ['review_text', 'rating', 'date', 'bank', 'source']
    has_all_columns = all(col in df.columns for col in required_columns)
    print(f'\n✓ Has all required columns: {has_all_columns}')
    
    if not has_all_columns:
        return False
    
    # Verify KPIs
    print(f'\n=== KPI VERIFICATION ===')
    total_reviews = len(df)
    kpi_pass = total_reviews >= 1200
    print(f'Total reviews: {total_reviews} (Target: 1,200+) {"✅" if kpi_pass else "❌"}')
    
    reviews_per_bank = df['bank'].value_counts()
    print(f'\nReviews per bank:')
    all_banks_pass = True
    for bank, count in reviews_per_bank.items():
        status = "✅" if count >= 400 else "⚠️"
        if count < 400:
            all_banks_pass = False
        print(f'  {status} {bank}: {count} (Target: 400+)')
    
    missing_data_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    missing_pass = missing_data_pct < 5
    print(f'\nMissing data: {missing_data_pct:.2f}% (Target: <5%) {"✅" if missing_pass else "❌"}')
    
    all_passed = kpi_pass and all_banks_pass and missing_pass
    if all_passed:
        print('\n✅ Dataset verification complete! All KPIs met.')
    else:
        print('\n⚠️  Dataset verification complete! Some KPIs not fully met.')
    
    return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape and preprocess Google Play Store reviews')
    parser.add_argument('--verify-only', action='store_true', 
                       help='Only verify existing dataset without scraping')
    parser.add_argument('--verify', action='store_true',
                       help='Verify dataset after scraping')
    
    args = parser.parse_args()
    
    if args.verify_only:
        # Only verify existing dataset
        verify_dataset()
    else:
        # Run the scraping and preprocessing
        final_dataset = scrape_all_reviews()
        
        if not final_dataset.empty:
            print("\n✅ Task 1 completed successfully!")
            
            # Verify if requested
            if args.verify:
                verify_dataset()
        else:
            print("\n❌ Task 1 failed - no data collected.")
            sys.exit(1)

