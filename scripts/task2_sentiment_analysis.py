"""
Task 2: Sentiment and Thematic Analysis

Main script to perform comprehensive sentiment analysis and thematic analysis
on banking app reviews.
"""

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from text_preprocessor import TextPreprocessor
from sentiment_analyzer import SentimentAnalyzer
from keyword_extractor import KeywordExtractor
from theme_analyzer import ThemeAnalyzer

import warnings
warnings.filterwarnings('ignore')


def load_data(data_path: str = 'data/cleaned/clean_reviews.csv') -> pd.DataFrame:
    """Load the cleaned reviews dataset."""
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Add review_id if it doesn't exist
    if 'review_id' not in df.columns:
        df['review_id'] = range(1, len(df) + 1)
    
    print(f"Loaded {len(df)} reviews")
    print(f"Banks: {df['bank'].unique()}")
    print(f"Bank counts:\n{df['bank'].value_counts()}")
    
    return df


def main():
    """Main analysis pipeline."""
    print("=" * 80)
    print("TASK 2: SENTIMENT & THEMATIC ANALYSIS")
    print("=" * 80)
    print()
    
    # Load data
    df = load_data()
    
    # Step 1: NLP Preprocessing
    print("\n" + "=" * 80)
    print("STEP 1: NLP PREPROCESSING")
    print("=" * 80)
    preprocessor = TextPreprocessor(remove_stopwords=True, lemmatize=True)
    df = preprocessor.preprocess_dataframe(df, text_column='review_text')
    print(f"✓ Preprocessed {len(df)} reviews")
    print(f"✓ Sample cleaned text: {df['cleaned_text'].iloc[0][:100]}...")
    
    # Step 2: Sentiment Analysis
    print("\n" + "=" * 80)
    print("STEP 2: SENTIMENT ANALYSIS")
    print("=" * 80)
    sentiment_analyzer = SentimentAnalyzer()
    df = sentiment_analyzer.analyze_dataframe(df, text_column='review_text')
    
    # Compare with ratings
    df = sentiment_analyzer.compare_with_rating(df)
    
    print(f"✓ Analyzed sentiment for {len(df)} reviews")
    print(f"\nSentiment Distribution:")
    print(df['sentiment_label'].value_counts())
    print(f"\nSentiment-Rating Match:")
    print(df['sentiment_rating_match'].value_counts())
    
    # Step 3: Keyword Extraction
    print("\n" + "=" * 80)
    print("STEP 3: KEYWORD & N-GRAM EXTRACTION")
    print("=" * 80)
    keyword_extractor = KeywordExtractor()
    
    # Extract keywords per bank
    keywords_by_bank = keyword_extractor.extract_keywords_per_bank(
        df, text_column='cleaned_text', bank_column='bank', top_n=50
    )
    
    print("\nTop keywords per bank:")
    for bank, keywords in keywords_by_bank.items():
        print(f"\n{bank}:")
        for kw, score in keywords[:10]:
            print(f"  - {kw}: {score:.4f}")
    
    # Extract complaint and praise keywords
    complaint_keywords = keyword_extractor.extract_complaint_keywords(
        df, text_column='cleaned_text', top_n=30
    )
    praise_keywords = keyword_extractor.extract_praise_keywords(
        df, text_column='cleaned_text', top_n=30
    )
    
    print(f"\n✓ Top complaint keywords: {len(complaint_keywords)}")
    print(f"✓ Top praise keywords: {len(praise_keywords)}")
    
    # Extract keywords for each review
    print("\nExtracting keywords for individual reviews...")
    df['keywords'] = df['cleaned_text'].apply(
        lambda x: keyword_extractor.extract_keywords_for_review(x, top_n=10)
    )
    df['keywords_str'] = df['keywords'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
    
    # Step 4: Thematic Analysis
    print("\n" + "=" * 80)
    print("STEP 4: THEMATIC ANALYSIS")
    print("=" * 80)
    theme_analyzer = ThemeAnalyzer()
    
    # Analyze themes per bank
    theme_analysis = theme_analyzer.analyze_themes_per_bank(
        df, text_column='review_text', bank_column='bank', keywords_column='keywords'
    )
    
    print("\nTheme analysis per bank:")
    for bank, analysis in theme_analysis.items():
        print(f"\n{bank}:")
        print(f"  Total reviews: {analysis['total_reviews']}")
        print(f"  Themes identified: {len(analysis['themes'])}")
        for theme_name, theme_data in analysis['themes'].items():
            print(f"    - {theme_name}: {theme_data['frequency']} reviews ({theme_data['percentage']:.1f}%) - {theme_data['severity']} severity")
    
    # Identify themes for each review
    print("\nIdentifying themes for individual reviews...")
    df['identified_themes'] = df.apply(
        lambda row: theme_analyzer.identify_theme_for_review(
            row['review_text'],
            row['keywords'] if isinstance(row['keywords'], list) else []
        ),
        axis=1
    )
    df['identified_themes_str'] = df['identified_themes'].apply(
        lambda x: '; '.join(x) if isinstance(x, list) and x else 'No Theme'
    )
    
    # Step 5: Prepare output CSV
    print("\n" + "=" * 80)
    print("STEP 5: PREPARING OUTPUT CSV")
    print("=" * 80)
    
    # Create output DataFrame with required columns
    output_df = pd.DataFrame({
        'review_id': df['review_id'],
        'bank_name': df['bank'],
        'review_text': df['review_text'],
        'rating': df['rating'],
        'sentiment_label': df['sentiment_label'],
        'sentiment_score': df['sentiment_score'].round(4),
        'identified_theme(s)': df['identified_themes_str'],
        'keywords': df['keywords_str']
    })
    
    # Save to CSV
    output_path = 'data/processed/task2_sentiment_analysis_results.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, index=False)
    print(f"✓ Saved results to {output_path}")
    print(f"✓ Total rows: {len(output_df)}")
    
    # Step 6: Generate summary statistics
    print("\n" + "=" * 80)
    print("STEP 6: SUMMARY STATISTICS")
    print("=" * 80)
    
    # Global statistics
    print("\n=== GLOBAL ANALYSIS ===")
    print(f"Total reviews analyzed: {len(df)}")
    print(f"\nSentiment Distribution:")
    sentiment_dist = df['sentiment_label'].value_counts(normalize=True) * 100
    for label, pct in sentiment_dist.items():
        print(f"  {label}: {pct:.2f}%")
    
    print(f"\nRating Distribution:")
    rating_dist = df['rating'].value_counts(normalize=True) * 100
    for rating, pct in sorted(rating_dist.items()):
        print(f"  {rating} stars: {pct:.2f}%")
    
    # Per-bank statistics
    print("\n=== PER-BANK ANALYSIS ===")
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        print(f"\n{bank}:")
        print(f"  Total reviews: {len(bank_df)}")
        print(f"  Mean sentiment score: {bank_df['sentiment_score'].mean():.4f}")
        print(f"  Sentiment distribution:")
        bank_sentiment = bank_df['sentiment_label'].value_counts(normalize=True) * 100
        for label, pct in bank_sentiment.items():
            print(f"    {label}: {pct:.2f}%")
        print(f"  Rating distribution:")
        bank_rating = bank_df['rating'].value_counts(normalize=True) * 100
        for rating, pct in sorted(bank_rating.items()):
            print(f"    {rating} stars: {pct:.2f}%")
    
    # Theme statistics
    print("\n=== THEME STATISTICS ===")
    all_themes = []
    for themes_list in df['identified_themes']:
        if isinstance(themes_list, list):
            all_themes.extend(themes_list)
    theme_counts = pd.Series(all_themes).value_counts()
    print("\nTop themes across all banks:")
    for theme, count in theme_counts.head(10).items():
        print(f"  {theme}: {count} reviews")
    
    # KPI Check
    print("\n" + "=" * 80)
    print("KPI VERIFICATION")
    print("=" * 80)
    
    sentiment_coverage = (df['sentiment_label'].notna().sum() / len(df)) * 100
    min_reviews = len(df) >= 400
    themes_per_bank = {bank: len(analysis['themes']) for bank, analysis in theme_analysis.items()}
    min_themes = all(count >= 2 for count in themes_per_bank.values())
    
    print(f"✓ Sentiment computed for {sentiment_coverage:.1f}% of reviews (Target: 90%+)")
    print(f"✓ Minimum 400 reviews: {min_reviews} (Actual: {len(df)})")
    print(f"✓ At least 2 themes per bank: {min_themes}")
    for bank, count in themes_per_bank.items():
        print(f"    {bank}: {count} themes")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nOutput saved to: {output_path}")
    print(f"\nNext step: Generate detailed report using generate_report.py")
    
    return df, theme_analysis, keywords_by_bank


if __name__ == "__main__":
    df, theme_analysis, keywords_by_bank = main()

