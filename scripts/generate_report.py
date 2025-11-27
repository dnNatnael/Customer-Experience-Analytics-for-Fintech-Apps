"""
Generate comprehensive report with analysis results.
"""

import sys
import os
import pandas as pd
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from theme_analyzer import ThemeAnalyzer


def load_results(csv_path: str = 'data/processed/sentiment_analysis_results.csv'):
    """Load analysis results."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Results file not found: {csv_path}. Please run sentiment_analysis.py first.")
    
    return pd.read_csv(csv_path)


def generate_report(df: pd.DataFrame, output_path: str = 'reports/task2_sentiment_theme.md'):
    """Generate comprehensive markdown report."""
    
    theme_analyzer = ThemeAnalyzer()
    
    # Re-analyze themes for detailed report
    theme_analysis = theme_analyzer.analyze_themes_per_bank(
        df, text_column='review_text', bank_column='bank_name'
    )
    
    report = []
    report.append("# Task 2: Sentiment & Thematic Analysis Report\n")
    report.append("**Generated:** " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    report.append("\n---\n")
    
    # Executive Summary
    report.append("## 1. Executive Summary\n")
    report.append(f"This report presents a comprehensive sentiment and thematic analysis of **{len(df)} reviews** ")
    report.append(f"across **{df['bank_name'].nunique()} banking apps** from the Google Play Store.\n\n")
    
    # Global Analysis
    report.append("## 2. Global Analysis Summary\n\n")
    
    # Overall sentiment distribution
    report.append("### 2.1 Overall Sentiment Distribution\n\n")
    sentiment_dist = df['sentiment_label'].value_counts()
    sentiment_pct = df['sentiment_label'].value_counts(normalize=True) * 100
    
    report.append("| Sentiment | Count | Percentage |\n")
    report.append("|-----------|-------|------------|\n")
    for label in ['Positive', 'Negative', 'Neutral']:
        if label in sentiment_dist:
            report.append(f"| {label} | {sentiment_dist[label]} | {sentiment_pct[label]:.2f}% |\n")
    
    report.append(f"\n**Mean Sentiment Score:** {df['sentiment_score'].mean():.4f}\n\n")
    
    # Rating distribution
    report.append("### 2.2 Rating Distribution\n\n")
    rating_dist = df['rating'].value_counts().sort_index()
    rating_pct = df['rating'].value_counts(normalize=True).sort_index() * 100
    
    report.append("| Rating | Count | Percentage |\n")
    report.append("|--------|-------|------------|\n")
    for rating in sorted(rating_dist.index):
        report.append(f"| {rating} ⭐ | {rating_dist[rating]} | {rating_pct[rating]:.2f}% |\n")
    
    # Sentiment-Rating Comparison
    report.append("\n### 2.3 Sentiment vs Rating Comparison\n\n")
    report.append("Analysis of alignment between sentiment scores and star ratings:\n\n")
    
    # Anomalies (positive sentiment but low rating, or negative sentiment but high rating)
    anomalies = df[
        ((df['sentiment_label'] == 'Positive') & (df['rating'] <= 2)) |
        ((df['sentiment_label'] == 'Negative') & (df['rating'] >= 4))
    ]
    
    report.append(f"**Anomalies Found:** {len(anomalies)} reviews ({len(anomalies)/len(df)*100:.2f}%)\n\n")
    if len(anomalies) > 0:
        report.append("Sample anomalies:\n\n")
        for idx, row in anomalies.head(5).iterrows():
            report.append(f"- **Rating {row['rating']}** | **Sentiment: {row['sentiment_label']}** | {row['review_text'][:100]}...\n")
        report.append("\n")
    
    # Top themes across all banks
    report.append("### 2.4 Top Themes Across All Banks\n\n")
    all_themes = []
    for themes_str in df['identified_theme(s)']:
        if pd.notna(themes_str) and themes_str != 'No Theme':
            themes = [t.strip() for t in str(themes_str).split(';')]
            all_themes.extend(themes)
    
    theme_counts = pd.Series(all_themes).value_counts()
    report.append("| Theme | Frequency | Percentage |\n")
    report.append("|-------|-----------|------------|\n")
    for theme, count in theme_counts.head(10).items():
        pct = (count / len(df)) * 100
        report.append(f"| {theme} | {count} | {pct:.2f}% |\n")
    
    # Per-Bank Analysis
    report.append("\n---\n")
    report.append("## 3. Per-Bank Detailed Analysis\n\n")
    
    for bank in sorted(df['bank_name'].unique()):
        bank_df = df[df['bank_name'] == bank]
        bank_analysis = theme_analysis.get(bank, {})
        
        report.append(f"### 3.{list(df['bank_name'].unique()).index(bank) + 1} {bank}\n\n")
        
        # Bank overview
        report.append("#### Overview\n\n")
        report.append(f"- **Total Reviews:** {len(bank_df)}\n")
        report.append(f"- **Mean Sentiment Score:** {bank_df['sentiment_score'].mean():.4f}\n")
        report.append(f"- **Mean Rating:** {bank_df['rating'].mean():.2f} ⭐\n\n")
        
        # Sentiment distribution
        report.append("#### Sentiment Distribution\n\n")
        bank_sentiment = bank_df['sentiment_label'].value_counts()
        bank_sentiment_pct = bank_df['sentiment_label'].value_counts(normalize=True) * 100
        
        report.append("| Sentiment | Count | Percentage |\n")
        report.append("|-----------|-------|------------|\n")
        for label in ['Positive', 'Negative', 'Neutral']:
            if label in bank_sentiment:
                report.append(f"| {label} | {bank_sentiment[label]} | {bank_sentiment_pct[label]:.2f}% |\n")
        
        # Rating distribution
        report.append("\n#### Rating Distribution\n\n")
        bank_rating = bank_df['rating'].value_counts().sort_index()
        bank_rating_pct = bank_df['rating'].value_counts(normalize=True).sort_index() * 100
        
        report.append("| Rating | Count | Percentage |\n")
        report.append("|--------|-------|------------|\n")
        for rating in sorted(bank_rating.index):
            report.append(f"| {rating} ⭐ | {bank_rating[rating]} | {bank_rating_pct[rating]:.2f}% |\n")
        
        # Themes
        report.append("\n#### Identified Themes\n\n")
        if bank_analysis and 'themes' in bank_analysis:
            themes = bank_analysis['themes']
            if themes:
                for theme_name, theme_data in themes.items():
                    report.append(f"##### {theme_name}\n\n")
                    report.append(f"- **Frequency:** {theme_data['frequency']} reviews ({theme_data['percentage']:.1f}%)\n")
                    report.append(f"- **Severity:** {theme_data['severity']}\n")
                    report.append(f"- **Supporting Keywords:** {', '.join(theme_data['supporting_keywords'][:10])}\n\n")
                    
                    # Representative reviews
                    report.append("**Representative Reviews:**\n\n")
                    for i, review in enumerate(theme_data['representative_reviews'][:3], 1):
                        review_text = review.get('review_text', '')[:200]
                        rating = review.get('rating', 'N/A')
                        sentiment = review.get('sentiment', 'N/A')
                        report.append(f"{i}. **Rating: {rating}** | **Sentiment: {sentiment}**\n")
                        report.append(f"   > {review_text}...\n\n")
            else:
                report.append("No themes identified for this bank.\n\n")
        else:
            report.append("Theme analysis not available.\n\n")
        
        # Top keywords
        report.append("#### Top Keywords\n\n")
        # Extract keywords for this bank
        bank_keywords = []
        for keywords_str in bank_df['keywords']:
            if pd.notna(keywords_str):
                keywords = [k.strip() for k in str(keywords_str).split(',')]
                bank_keywords.extend(keywords)
        
        keyword_counts = pd.Series(bank_keywords).value_counts()
        report.append("| Keyword | Frequency |\n")
        report.append("|---------|-----------|\n")
        for keyword, count in keyword_counts.head(15).items():
            report.append(f"| {keyword} | {count} |\n")
        
        # Actionable recommendations
        report.append("\n#### Actionable Recommendations\n\n")
        
        # Generate recommendations based on themes
        if bank_analysis and 'themes' in bank_analysis:
            themes = bank_analysis['themes']
            high_severity_themes = [name for name, data in themes.items() if data['severity'] == 'High']
            medium_severity_themes = [name for name, data in themes.items() if data['severity'] == 'Medium']
            
            if high_severity_themes:
                report.append("**High Priority Issues:**\n\n")
                for theme in high_severity_themes:
                    report.append(f"- **{theme}:** Address immediately. {themes[theme]['frequency']} reviews mention this issue.\n")
                report.append("\n")
            
            if medium_severity_themes:
                report.append("**Medium Priority Issues:**\n\n")
                for theme in medium_severity_themes:
                    report.append(f"- **{theme}:** Monitor and plan improvements. {themes[theme]['frequency']} reviews mention this issue.\n")
                report.append("\n")
        
        # Positive feedback
        positive_reviews = bank_df[bank_df['sentiment_label'] == 'Positive']
        if len(positive_reviews) > 0:
            report.append("**Strengths to Maintain:**\n\n")
            positive_keywords = []
            for keywords_str in positive_reviews['keywords']:
                if pd.notna(keywords_str):
                    keywords = [k.strip() for k in str(keywords_str).split(',')]
                    positive_keywords.extend(keywords)
            positive_keyword_counts = pd.Series(positive_keywords).value_counts()
            for keyword, count in positive_keyword_counts.head(5).items():
                report.append(f"- **{keyword}** (mentioned in {count} positive reviews)\n")
            report.append("\n")
        
        report.append("---\n\n")
    
    # Methodology
    report.append("## 4. Methodology\n\n")
    report.append("### 4.1 Sentiment Analysis\n\n")
    report.append("Sentiment analysis was performed using the following models (in priority order):\n\n")
    report.append("1. **DistilBERT** (distilbert-base-uncased-finetuned-sst-2-english) - Primary model\n")
    report.append("2. **VADER** - Fallback for comparison\n")
    report.append("3. **TextBlob** - Additional fallback\n\n")
    report.append("Each review was assigned a sentiment label (Positive/Negative/Neutral) and a confidence score (0-1).\n\n")
    
    report.append("### 4.2 NLP Preprocessing\n\n")
    report.append("The following preprocessing steps were applied to all reviews:\n\n")
    report.append("- Lowercasing\n")
    report.append("- Tokenization\n")
    report.append("- Stop-word removal\n")
    report.append("- Lemmatization (using spaCy)\n")
    report.append("- Bigram and trigram phrase detection\n\n")
    
    report.append("### 4.3 Keyword Extraction\n\n")
    report.append("Keywords were extracted using:\n\n")
    report.append("- **TF-IDF** (Term Frequency-Inverse Document Frequency) for 1- to 3-grams\n")
    report.append("- **spaCy noun-chunk extraction** for phrase identification\n\n")
    
    report.append("### 4.4 Thematic Analysis\n\n")
    report.append("Themes were identified by:\n\n")
    report.append("1. Mapping extracted keywords to predefined theme categories\n")
    report.append("2. Pattern matching against theme-specific keywords and patterns\n")
    report.append("3. Frequency analysis to determine theme prevalence\n")
    report.append("4. Severity assessment based on sentiment and rating distribution within each theme\n\n")
    
    report.append("### 4.5 Theme Categories\n\n")
    report.append("The following theme categories were used:\n\n")
    report.append("- Account Access Issues\n")
    report.append("- Transaction Performance\n")
    report.append("- Stability & Reliability\n")
    report.append("- User Interface & Experience\n")
    report.append("- Customer Support\n")
    report.append("- Feature Requests\n")
    report.append("- Security Concerns\n")
    report.append("- Network & Connectivity\n\n")
    
    # KPI Verification
    report.append("## 5. KPI Verification\n\n")
    
    sentiment_coverage = (df['sentiment_label'].notna().sum() / len(df)) * 100
    min_reviews = len(df) >= 400
    
    report.append("| KPI | Target | Achieved | Status |\n")
    report.append("|-----|--------|----------|--------|\n")
    report.append(f"| Sentiment computed | 90%+ | {sentiment_coverage:.1f}% | {'✅ PASS' if sentiment_coverage >= 90 else '❌ FAIL'} |\n")
    report.append(f"| Minimum reviews | 400+ | {len(df)} | {'✅ PASS' if min_reviews else '❌ FAIL'} |\n")
    
    # Themes per bank
    for bank in df['bank_name'].unique():
        bank_analysis = theme_analysis.get(bank, {})
        theme_count = len(bank_analysis.get('themes', {}))
        report.append(f"| Themes for {bank} | 2+ | {theme_count} | {'✅ PASS' if theme_count >= 2 else '❌ FAIL'} |\n")
    
    # Conclusion
    report.append("\n## 6. Conclusion\n\n")
    report.append("This analysis provides comprehensive insights into customer sentiment and key themes ")
    report.append("across banking app reviews. The findings can be used to:\n\n")
    report.append("- Identify critical issues requiring immediate attention\n")
    report.append("- Understand customer satisfaction drivers\n")
    report.append("- Prioritize product development efforts\n")
    report.append("- Improve customer experience and app performance\n\n")
    
    report.append("---\n\n")
    report.append("**Report Generated:** " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
    
    # Write report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    print(f"✓ Report generated: {output_path}")
    return output_path


if __name__ == "__main__":
    print("Loading analysis results...")
    df = load_results()
    
    print("Generating comprehensive report...")
    report_path = generate_report(df)
    
    print(f"\n✓ Report saved to: {report_path}")

