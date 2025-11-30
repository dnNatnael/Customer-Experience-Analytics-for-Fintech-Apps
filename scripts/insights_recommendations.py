"""
Task 4: Insights & Recommendations
Analyzes customer reviews for CBE, BOA, and Dashen Bank to generate
insights, visualizations, and actionable recommendations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Bank name mappings
BANK_MAPPING = {
    'Commercial Bank of Ethiopia': 'CBE',
    'Bank of Abyssinia': 'BOA',
    'Dashen Bank': 'Dashen'
}

# Target banks (only these three)
TARGET_BANKS = ['Commercial Bank of Ethiopia', 'Bank of Abyssinia', 'Dashen Bank']


def load_data(data_path: str = 'data/processed/sentiment_analysis_results.csv') -> pd.DataFrame:
    """Load and filter data for only CBE, BOA, and Dashen."""
    print("📂 Loading data...")
    df = pd.read_csv(data_path)
    
    # Filter for only target banks
    initial_count = len(df)
    df = df[df['bank_name'].isin(TARGET_BANKS)].copy()
    filtered_count = len(df)
    
    print(f"  ✓ Loaded {filtered_count} reviews (filtered from {initial_count} total)")
    print(f"  ✓ Banks: {df['bank_name'].unique().tolist()}")
    
    # Standardize bank names to short codes
    df['bank_code'] = df['bank_name'].map(BANK_MAPPING)
    
    # Clean theme column (handle NaN and "No Theme")
    df['theme'] = df['identified_theme(s)'].fillna('No Theme')
    df['theme'] = df['theme'].replace('No Theme', 'Uncategorized')
    
    # Ensure numeric columns are correct types
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
    
    return df


def extract_keywords_from_text(text: str) -> list:
    """Extract meaningful keywords from review text."""
    if pd.isna(text) or text == '':
        return []
    
    # Common positive words
    positive_words = ['good', 'great', 'excellent', 'fast', 'easy', 'convenient', 
                     'smooth', 'nice', 'love', 'best', 'perfect', 'quick', 'simple']
    
    # Common negative words
    negative_words = ['bad', 'slow', 'crash', 'error', 'problem', 'issue', 'bug',
                     'fail', 'broken', 'terrible', 'worst', 'awful', 'frustrating']
    
    text_lower = str(text).lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Filter for meaningful words (length > 3)
    keywords = [w for w in words if len(w) > 3]
    
    # Add sentiment-based keywords
    all_keywords = []
    for word in keywords:
        if word in positive_words:
            all_keywords.append(f"positive_{word}")
        elif word in negative_words:
            all_keywords.append(f"negative_{word}")
        else:
            all_keywords.append(word)
    
    return all_keywords


def analyze_satisfaction_drivers(df: pd.DataFrame, bank_name: str) -> dict:
    """Identify customer satisfaction drivers for a specific bank."""
    bank_df = df[df['bank_name'] == bank_name].copy()
    
    # Filter for positive reviews (rating >= 4 or sentiment = Positive)
    positive_reviews = bank_df[
        (bank_df['rating'] >= 4) | (bank_df['sentiment_label'] == 'Positive')
    ].copy()
    
    drivers = {
        'themes': {},
        'keywords': {},
        'sample_reviews': []
    }
    
    # Analyze themes in positive reviews
    theme_counts = positive_reviews['theme'].value_counts()
    for theme, count in theme_counts.head(5).items():
        if theme != 'Uncategorized':
            drivers['themes'][theme] = {
                'count': int(count),
                'percentage': round(count / len(positive_reviews) * 100, 1)
            }
    
    # Extract keywords from positive reviews
    all_keywords = []
    for text in positive_reviews['review_text'].dropna():
        keywords = extract_keywords_from_text(text)
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    for keyword, count in keyword_counts.most_common(10):
        if 'positive_' in keyword or count >= 3:
            drivers['keywords'][keyword.replace('positive_', '')] = count
    
    # Get sample positive reviews
    sample_reviews = positive_reviews.nlargest(3, 'sentiment_score')['review_text'].tolist()
    drivers['sample_reviews'] = sample_reviews[:3]
    
    return drivers


def analyze_pain_points(df: pd.DataFrame, bank_name: str) -> dict:
    """Identify customer pain points for a specific bank."""
    bank_df = df[df['bank_name'] == bank_name].copy()
    
    # Filter for negative reviews (rating <= 2 or sentiment = Negative)
    negative_reviews = bank_df[
        (bank_df['rating'] <= 2) | (bank_df['sentiment_label'] == 'Negative')
    ].copy()
    
    pain_points = {
        'themes': {},
        'keywords': {},
        'sample_reviews': []
    }
    
    # Analyze themes in negative reviews
    theme_counts = negative_reviews['theme'].value_counts()
    for theme, count in theme_counts.head(5).items():
        if theme != 'Uncategorized':
            pain_points['themes'][theme] = {
                'count': int(count),
                'percentage': round(count / len(negative_reviews) * 100, 1)
            }
    
    # Extract keywords from negative reviews
    all_keywords = []
    for text in negative_reviews['review_text'].dropna():
        keywords = extract_keywords_from_text(text)
        all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    for keyword, count in keyword_counts.most_common(10):
        if 'negative_' in keyword or count >= 3:
            pain_points['keywords'][keyword.replace('negative_', '')] = count
    
    # Get sample negative reviews
    sample_reviews = negative_reviews.nsmallest(3, 'sentiment_score')['review_text'].tolist()
    pain_points['sample_reviews'] = sample_reviews[:3]
    
    return pain_points


def create_sentiment_distribution_plot(df: pd.DataFrame, output_dir: Path):
    """Create sentiment distribution bar chart per bank."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare data
    sentiment_data = []
    for bank in TARGET_BANKS:
        bank_df = df[df['bank_name'] == bank]
        for sentiment in ['Positive', 'Neutral', 'Negative']:
            count = len(bank_df[bank_df['sentiment_label'] == sentiment])
            sentiment_data.append({
                'Bank': BANK_MAPPING[bank],
                'Sentiment': sentiment,
                'Count': count
            })
    
    sentiment_df = pd.DataFrame(sentiment_data)
    
    # Create grouped bar chart
    sentiment_pivot = sentiment_df.pivot(index='Bank', columns='Sentiment', values='Count')
    sentiment_pivot.plot(kind='bar', ax=ax, color=['#2ecc71', '#f39c12', '#e74c3c'], width=0.8)
    
    ax.set_title('Sentiment Distribution by Bank', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Bank', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
    ax.legend(title='Sentiment', title_fontsize=11, fontsize=10)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'sentiment_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Created sentiment_distribution.png")


def create_rating_distribution_plot(df: pd.DataFrame, output_dir: Path):
    """Create rating distribution plot per bank."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, bank in enumerate(TARGET_BANKS):
        bank_df = df[df['bank_name'] == bank]
        rating_counts = bank_df['rating'].value_counts().sort_index()
        
        axes[idx].bar(rating_counts.index, rating_counts.values, 
                     color=['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#2ecc71'],
                     alpha=0.7, edgecolor='black', linewidth=1.2)
        
        axes[idx].set_title(f'{BANK_MAPPING[bank]}', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Rating', fontsize=10)
        axes[idx].set_ylabel('Count', fontsize=10)
        axes[idx].set_xticks([1, 2, 3, 4, 5])
        axes[idx].grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for i, v in enumerate(rating_counts.values):
            axes[idx].text(rating_counts.index[i], v + 1, str(v), 
                          ha='center', va='bottom', fontweight='bold')
    
    fig.suptitle('Rating Distribution by Bank', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'rating_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Created rating_distribution.png")


def create_theme_frequency_plot(df: pd.DataFrame, output_dir: Path):
    """Create theme frequency bar chart per bank."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get top themes across all banks
    all_themes = df[df['theme'] != 'Uncategorized']['theme'].value_counts().head(8).index.tolist()
    
    # Prepare data
    theme_data = []
    for bank in TARGET_BANKS:
        bank_df = df[df['bank_name'] == bank]
        for theme in all_themes:
            count = len(bank_df[bank_df['theme'] == theme])
            theme_data.append({
                'Bank': BANK_MAPPING[bank],
                'Theme': theme,
                'Count': count
            })
    
    theme_df = pd.DataFrame(theme_data)
    
    # Create grouped bar chart
    theme_pivot = theme_df.pivot(index='Theme', columns='Bank', values='Count')
    theme_pivot = theme_pivot.fillna(0)
    
    theme_pivot.plot(kind='barh', ax=ax, color=['#3498db', '#2ecc71', '#e67e22'], width=0.8)
    
    ax.set_title('Top Theme Frequency by Bank', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Number of Reviews', fontsize=12, fontweight='bold')
    ax.set_ylabel('Theme', fontsize=12, fontweight='bold')
    ax.legend(title='Bank', title_fontsize=11, fontsize=10)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'theme_frequency.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Created theme_frequency.png")


def create_sentiment_over_time_plot(df: pd.DataFrame, output_dir: Path):
    """Create sentiment trend over time (if dates available)."""
    # Check if we have date information
    # Since dates might not be in processed data, create a synthetic time-based analysis
    # based on review_id or create monthly aggregates if possible
    
    # For now, create a comparison chart showing sentiment scores by bank
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calculate average sentiment score by bank
    bank_sentiment = df.groupby('bank_name')['sentiment_score'].agg(['mean', 'std']).reset_index()
    bank_sentiment['bank_code'] = bank_sentiment['bank_name'].map(BANK_MAPPING)
    
    x_pos = np.arange(len(bank_sentiment))
    bars = ax.bar(x_pos, bank_sentiment['mean'], 
                  yerr=bank_sentiment['std'],
                  color=['#3498db', '#2ecc71', '#e67e22'],
                  alpha=0.7, edgecolor='black', linewidth=1.2,
                  capsize=5, capthick=2)
    
    ax.set_title('Average Sentiment Score by Bank', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Bank', fontsize=12, fontweight='bold')
    ax.set_ylabel('Sentiment Score', fontsize=12, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bank_sentiment['bank_code'])
    ax.set_ylim(0, 1)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (bar, mean_val) in enumerate(zip(bars, bank_sentiment['mean'])):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
               f'{mean_val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'sentiment_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Created sentiment_comparison.png")


def create_wordcloud_plot(df: pd.DataFrame, output_dir: Path):
    """Create word clouds for positive vs negative reviews (optional)."""
    try:
        from wordcloud import WordCloud
    except ImportError:
        print("  ⚠ wordcloud not available, skipping word cloud generation")
        return
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    for idx, bank in enumerate(TARGET_BANKS):
        bank_df = df[df['bank_name'] == bank]
        bank_code = BANK_MAPPING[bank]
        
        # Positive reviews
        positive_text = ' '.join(
            bank_df[(bank_df['rating'] >= 4) | (bank_df['sentiment_label'] == 'Positive')]
            ['review_text'].dropna().astype(str)
        )
        
        if positive_text:
            wordcloud_pos = WordCloud(width=400, height=300, 
                                     background_color='white',
                                     max_words=50).generate(positive_text)
            axes[0, idx].imshow(wordcloud_pos, interpolation='bilinear')
            axes[0, idx].set_title(f'{bank_code} - Positive Reviews', 
                                  fontsize=11, fontweight='bold')
            axes[0, idx].axis('off')
        
        # Negative reviews
        negative_text = ' '.join(
            bank_df[(bank_df['rating'] <= 2) | (bank_df['sentiment_label'] == 'Negative')]
            ['review_text'].dropna().astype(str)
        )
        
        if negative_text:
            wordcloud_neg = WordCloud(width=400, height=300,
                                     background_color='white',
                                     max_words=50).generate(negative_text)
            axes[1, idx].imshow(wordcloud_neg, interpolation='bilinear')
            axes[1, idx].set_title(f'{bank_code} - Negative Reviews',
                                  fontsize=11, fontweight='bold')
            axes[1, idx].axis('off')
    
    plt.suptitle('Word Clouds: Positive vs Negative Reviews by Bank', 
                fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(output_dir / 'wordclouds.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Created wordclouds.png")


def generate_insights_report(df: pd.DataFrame, output_dir: Path) -> str:
    """Generate comprehensive insights report."""
    report = []
    report.append("# Task 4: Insights & Recommendations Report\n")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n")
    
    # Executive Summary
    report.append("## 1. Executive Summary\n")
    total_reviews = len(df)
    report.append(f"This report analyzes **{total_reviews} customer reviews** from Google Play Store ")
    report.append("for three Ethiopian banking apps:\n")
    report.append("- **CBE (Commercial Bank of Ethiopia)**\n")
    report.append("- **BOA (Bank of Abyssinia)**\n")
    report.append("- **Dashen Bank**\n\n")
    
    # Overall statistics
    report.append("### Overall Statistics\n\n")
    report.append("| Bank | Total Reviews | Avg Rating | Avg Sentiment Score |\n")
    report.append("|------|---------------|------------|---------------------|\n")
    
    for bank in TARGET_BANKS:
        bank_df = df[df['bank_name'] == bank]
        avg_rating = bank_df['rating'].mean()
        avg_sentiment = bank_df['sentiment_score'].mean()
        report.append(f"| {BANK_MAPPING[bank]} | {len(bank_df)} | {avg_rating:.2f} | {avg_sentiment:.3f} |\n")
    
    report.append("\n---\n")
    
    # Per-bank analysis
    report.append("## 2. Per-Bank Analysis\n\n")
    
    for bank in TARGET_BANKS:
        bank_code = BANK_MAPPING[bank]
        bank_df = df[df['bank_name'] == bank]
        
        report.append(f"### 2.{TARGET_BANKS.index(bank) + 1} {bank_code}\n\n")
        
        # Statistics
        report.append(f"**Total Reviews:** {len(bank_df)}\n")
        report.append(f"**Average Rating:** {bank_df['rating'].mean():.2f} ⭐\n")
        report.append(f"**Average Sentiment Score:** {bank_df['sentiment_score'].mean():.3f}\n\n")
        
        # Sentiment distribution
        sentiment_dist = bank_df['sentiment_label'].value_counts()
        report.append("**Sentiment Distribution:**\n")
        for sentiment, count in sentiment_dist.items():
            pct = count / len(bank_df) * 100
            report.append(f"- {sentiment}: {count} ({pct:.1f}%)\n")
        report.append("\n")
        
        # Satisfaction Drivers
        drivers = analyze_satisfaction_drivers(df, bank)
        report.append("#### Customer Satisfaction Drivers\n\n")
        
        if drivers['themes']:
            report.append("**Top Themes in Positive Reviews:**\n")
            for theme, data in list(drivers['themes'].items())[:3]:
                report.append(f"- **{theme}**: {data['count']} reviews ({data['percentage']}%)\n")
            report.append("\n")
        
        if drivers['keywords']:
            report.append("**Key Positive Keywords:**\n")
            for keyword, count in list(drivers['keywords'].items())[:5]:
                report.append(f"- {keyword} (mentioned {count} times)\n")
            report.append("\n")
        
        # Pain Points
        pain_points = analyze_pain_points(df, bank)
        report.append("#### Customer Pain Points\n\n")
        
        if pain_points['themes']:
            report.append("**Top Themes in Negative Reviews:**\n")
            for theme, data in list(pain_points['themes'].items())[:3]:
                report.append(f"- **{theme}**: {data['count']} reviews ({data['percentage']}%)\n")
            report.append("\n")
        
        if pain_points['keywords']:
            report.append("**Key Negative Keywords:**\n")
            for keyword, count in list(pain_points['keywords'].items())[:5]:
                report.append(f"- {keyword} (mentioned {count} times)\n")
            report.append("\n")
        
        report.append("---\n")
    
    # Cross-bank comparison
    report.append("## 3. Cross-Bank Comparison\n\n")
    
    # Rating comparison
    report.append("### 3.1 Rating Performance\n\n")
    report.append("| Bank | 5⭐ | 4⭐ | 3⭐ | 2⭐ | 1⭐ |\n")
    report.append("|------|----|----|----|----|----|\n")
    
    for bank in TARGET_BANKS:
        bank_df = df[df['bank_name'] == bank]
        rating_counts = bank_df['rating'].value_counts().sort_index()
        ratings_str = ' | '.join([str(rating_counts.get(i, 0)) for i in [5, 4, 3, 2, 1]])
        report.append(f"| {BANK_MAPPING[bank]} | {ratings_str} |\n")
    
    report.append("\n")
    
    # Theme comparison
    report.append("### 3.2 Theme Comparison\n\n")
    top_themes = df[df['theme'] != 'Uncategorized']['theme'].value_counts().head(5).index.tolist()
    
    report.append("| Theme | CBE | BOA | Dashen |\n")
    report.append("|-------|-----|-----|--------|\n")
    
    for theme in top_themes:
        counts = []
        for bank in TARGET_BANKS:
            bank_df = df[df['bank_name'] == bank]
            count = len(bank_df[bank_df['theme'] == theme])
            counts.append(str(count))
        report.append(f"| {theme} | {' | '.join(counts)} |\n")
    
    report.append("\n---\n")
    
    # Recommendations
    report.append("## 4. Actionable Recommendations\n\n")
    
    for bank in TARGET_BANKS:
        bank_code = BANK_MAPPING[bank]
        bank_df = df[df['bank_name'] == bank]
        pain_points = analyze_pain_points(df, bank)
        
        report.append(f"### 4.{TARGET_BANKS.index(bank) + 1} Recommendations for {bank_code}\n\n")
        
        # Generate recommendations based on pain points
        recommendations = []
        
        if 'Stability & Reliability' in pain_points['themes']:
            recommendations.append(
                "**Fix App Stability Issues:** Address frequent crashes and bugs. "
                "Implement comprehensive testing before releases and establish a "
                "robust error handling system."
            )
        
        if 'Transaction Performance' in pain_points['themes']:
            recommendations.append(
                "**Optimize Transaction Processing:** Improve transaction speed and "
                "reliability. Consider optimizing backend infrastructure and "
                "implementing better transaction status feedback."
            )
        
        if 'Account Access Issues' in pain_points['themes']:
            recommendations.append(
                "**Improve Authentication System:** Fix login timeout issues and "
                "authentication problems. Consider implementing biometric authentication "
                "and better session management."
            )
        
        if 'User Interface & Experience' in pain_points['themes']:
            recommendations.append(
                "**Enhance UI/UX Design:** Improve navigation speed and user interface "
                "clarity. Conduct user experience testing and implement user feedback "
                "in design iterations."
            )
        
        if 'Network & Connectivity' in pain_points['themes']:
            recommendations.append(
                "**Optimize Network Handling:** Improve app performance under poor "
                "network conditions. Implement better offline capabilities and "
                "connection retry mechanisms."
            )
        
        # Add generic recommendations if needed
        if len(recommendations) < 2:
            recommendations.append(
                "**Improve Error Messages:** Provide clearer, more actionable error "
                "messages to help users understand and resolve issues independently."
            )
            recommendations.append(
                "**Enhance Customer Support:** Establish better in-app support channels "
                "and response mechanisms to address user concerns promptly."
            )
        
        for i, rec in enumerate(recommendations[:3], 1):
            report.append(f"{i}. {rec}\n\n")
        
        report.append("---\n")
    
    # Ethics & Bias Reflection
    report.append("## 5. Ethics & Bias Reflection\n\n")
    
    report.append("### 5.1 Negative Review Bias\n\n")
    report.append(
        "Google Play Store reviews are inherently biased toward negative feedback. "
        "Users are more likely to leave reviews when they experience problems than "
        "when they have positive experiences. This can lead to an overrepresentation "
        "of complaints in the dataset, potentially skewing insights toward pain points "
        "rather than satisfaction drivers.\n\n"
    )
    
    report.append("### 5.2 App Version and Update Cycles\n\n")
    report.append(
        "Reviews may reflect experiences with different app versions, as users may "
        "not update their apps immediately. A review complaining about a bug that has "
        "already been fixed in a newer version could mislead analysis. Additionally, "
        "different banks may have different update frequencies, making direct "
        "comparisons challenging.\n\n"
    )
    
    report.append("### 5.3 Sample Demographics\n\n")
    report.append(
        "The dataset may not represent all user segments equally. Users who leave "
        "reviews may differ from the general user base in terms of technical "
        "proficiency, age, location, or engagement level. This demographic bias "
        "could affect the generalizability of insights.\n\n"
    )
    
    report.append("### 5.4 Limitations of Google Play Reviews\n\n")
    report.append(
        "Relying solely on Google Play Store reviews has several limitations:\n\n"
        "- **Language Bias:** Reviews are primarily in English, potentially missing "
        "feedback from users who prefer other languages.\n\n"
        "- **Selection Bias:** Only users who actively choose to leave reviews are "
        "represented, which may not reflect the silent majority.\n\n"
        "- **Temporal Bias:** Recent reviews may be overrepresented, while older "
        "reviews may reflect outdated app versions.\n\n"
        "- **Context Missing:** Reviews lack context about user's device, network "
        "conditions, or specific use cases that might affect their experience.\n\n"
    )
    
    report.append("---\n")
    
    # Conclusion
    report.append("## 6. Conclusion\n\n")
    report.append(
        "This analysis provides valuable insights into customer experiences with "
        "three major Ethiopian banking apps. While the findings highlight both "
        "strengths and areas for improvement, it is important to interpret these "
        "results within the context of the limitations discussed above. "
        "Recommendations should be validated through additional research methods, "
        "such as user surveys, usability testing, and direct customer feedback "
        "channels.\n\n"
    )
    
    return ''.join(report)


def main():
    """Main function to run Task 4 analysis."""
    print("="*60)
    print("Task 4: Insights & Recommendations")
    print("="*60)
    
    # Create output directory
    output_dir = Path('reports/visualizations')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    df = load_data()
    
    # Filter for only target banks (double-check)
    df = df[df['bank_name'].isin(TARGET_BANKS)].copy()
    
    print(f"\n📊 Dataset Summary:")
    print(f"  Total reviews: {len(df)}")
    for bank in TARGET_BANKS:
        bank_df = df[df['bank_name'] == bank]
        print(f"  {BANK_MAPPING[bank]}: {len(bank_df)} reviews")
    
    # Generate visualizations
    print("\n📈 Generating visualizations...")
    create_sentiment_distribution_plot(df, output_dir)
    create_rating_distribution_plot(df, output_dir)
    create_theme_frequency_plot(df, output_dir)
    create_sentiment_over_time_plot(df, output_dir)
    create_wordcloud_plot(df, output_dir)
    
    # Generate report
    print("\n📝 Generating insights report...")
    report_content = generate_insights_report(df, output_dir)
    
    # Save report
    report_path = Path('reports/task4_insights_recommendations.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"  ✓ Report saved to: {report_path}")
    
    print("\n" + "="*60)
    print("✅ Task 4 Complete!")
    print("="*60)
    print(f"\n📁 Outputs:")
    print(f"  - Report: {report_path}")
    print(f"  - Visualizations: {output_dir}/")
    print("\n")


if __name__ == '__main__':
    main()

