"""
Thematic Analysis Module

This module groups keywords and phrases into themes and identifies
recurring topics across reviews.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import Counter, defaultdict
import re


class ThemeAnalyzer:
    """Analyze themes from keywords and reviews."""
    
    # Theme keyword mappings (can be customized)
    THEME_KEYWORDS = {
        'Account Access Issues': {
            'keywords': ['login', 'password', 'otp', 'verification', 'access', 'unlock', 'locked', 
                        'authenticate', 'security', 'key', 'code', 'branch', 'verify', 'enter'],
            'patterns': [r'login', r'password', r'otp', r'verification', r'access', r'locked']
        },
        'Transaction Performance': {
            'keywords': ['transaction', 'transfer', 'payment', 'slow', 'failed', 'delay', 'timeout',
                        'process', 'complete', 'pending', 'stuck', 'wait', 'speed', 'fast'],
            'patterns': [r'transfer', r'payment', r'slow', r'failed', r'delay', r'timeout']
        },
        'Stability & Reliability': {
            'keywords': ['crash', 'bug', 'freeze', 'error', 'close', 'stop', 'work', 'broken',
                        'issue', 'problem', 'fix', 'update', 'version', 'hang'],
            'patterns': [r'crash', r'bug', r'freeze', r'error', r'broken', r'hang']
        },
        'User Interface & Experience': {
            'keywords': ['interface', 'design', 'layout', 'navigation', 'easy', 'simple', 'user',
                        'experience', 'ui', 'ux', 'confusing', 'difficult', 'hard', 'use'],
            'patterns': [r'interface', r'design', r'navigation', r'easy', r'simple', r'confusing']
        },
        'Customer Support': {
            'keywords': ['support', 'help', 'service', 'customer', 'response', 'contact', 'call',
                        'assist', 'resolve', 'unresolved', 'complaint', 'feedback'],
            'patterns': [r'support', r'help', r'service', r'response', r'contact']
        },
        'Feature Requests': {
            'keywords': ['feature', 'add', 'need', 'want', 'missing', 'request', 'improve',
                        'enhancement', 'suggestion', 'option', 'functionality', 'wallet'],
            'patterns': [r'feature', r'add', r'need', r'want', r'missing', r'improve']
        },
        'Security Concerns': {
            'keywords': ['security', 'safe', 'secure', 'privacy', 'data', 'protection', 'hack',
                        'fraud', 'risk', 'trust'],
            'patterns': [r'security', r'safe', r'secure', r'privacy']
        },
        'Network & Connectivity': {
            'keywords': ['network', 'connection', 'internet', 'wifi', 'data', 'connect', 'online',
                        'offline', 'signal', 'loading'],
            'patterns': [r'network', r'connection', r'internet', r'wifi', r'loading']
        }
    }
    
    def __init__(self):
        """Initialize theme analyzer."""
        pass
    
    def identify_theme_for_review(self, text: str, keywords: List[str] = None) -> List[str]:
        """
        Identify themes for a single review based on keywords and patterns.
        
        Args:
            text: Review text
            keywords: Optional list of keywords extracted from the review
            
        Returns:
            List of theme names that match the review
        """
        if not text or pd.isna(text):
            return []
        
        text_lower = text.lower()
        matched_themes = []
        theme_scores = defaultdict(int)
        
        # Check each theme
        for theme_name, theme_data in self.THEME_KEYWORDS.items():
            score = 0
            
            # Check keyword matches
            for keyword in theme_data['keywords']:
                if keyword in text_lower:
                    score += 1
            
            # Check pattern matches
            for pattern in theme_data['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 2  # Patterns are weighted higher
            
            # Also check provided keywords
            if keywords:
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    for theme_keyword in theme_data['keywords']:
                        if theme_keyword in keyword_lower or keyword_lower in theme_keyword:
                            score += 1
            
            theme_scores[theme_name] = score
        
        # Return themes with score >= 2 (at least one strong match)
        matched_themes = [theme for theme, score in theme_scores.items() if score >= 2]
        
        # If no themes match, return top theme by score
        if not matched_themes and theme_scores:
            top_theme = max(theme_scores.items(), key=lambda x: x[1])
            if top_theme[1] > 0:
                matched_themes = [top_theme[0]]
        
        return matched_themes
    
    def analyze_themes_per_bank(self, df: pd.DataFrame, text_column: str = 'review_text',
                                bank_column: str = 'bank', keywords_column: str = None) -> Dict[str, Dict]:
        """
        Analyze themes for each bank.
        
        Args:
            df: DataFrame with reviews
            text_column: Name of text column
            bank_column: Name of bank column
            keywords_column: Optional column name containing keywords for each review
            
        Returns:
            Dictionary mapping bank names to theme analysis results
        """
        theme_analysis = {}
        
        for bank in df[bank_column].unique():
            bank_df = df[df[bank_column] == bank].copy()
            
            # Identify themes for each review
            if keywords_column and keywords_column in bank_df.columns:
                bank_df['themes'] = bank_df.apply(
                    lambda row: self.identify_theme_for_review(
                        row[text_column],
                        eval(row[keywords_column]) if isinstance(row[keywords_column], str) else row[keywords_column]
                    ),
                    axis=1
                )
            else:
                bank_df['themes'] = bank_df[text_column].apply(self.identify_theme_for_review)
            
            # Count theme frequencies
            theme_counts = Counter()
            theme_reviews = defaultdict(list)
            
            for idx, row in bank_df.iterrows():
                themes = row['themes']
                for theme in themes:
                    theme_counts[theme] += 1
                    theme_reviews[theme].append({
                        'review_text': row[text_column],
                        'rating': row.get('rating', 'N/A'),
                        'sentiment': row.get('sentiment_label', 'N/A')
                    })
            
            # Get top themes (3-5)
            top_themes = theme_counts.most_common(5)
            
            # Build theme details
            theme_details = {}
            for theme_name, count in top_themes:
                if count > 0:  # Only include themes with matches
                    # Get representative reviews (mix of ratings)
                    reviews = theme_reviews[theme_name][:5]  # Top 5 representative reviews
                    
                    # Determine severity
                    severity = self._determine_severity(theme_reviews[theme_name], bank_df)
                    
                    # Get supporting keywords for this theme
                    supporting_keywords = self._extract_supporting_keywords(
                        theme_name, theme_reviews[theme_name]
                    )
                    
                    theme_details[theme_name] = {
                        'frequency': count,
                        'percentage': (count / len(bank_df)) * 100,
                        'severity': severity,
                        'supporting_keywords': supporting_keywords,
                        'representative_reviews': reviews
                    }
            
            theme_analysis[bank] = {
                'total_reviews': len(bank_df),
                'themes': theme_details
            }
        
        return theme_analysis
    
    def _determine_severity(self, reviews: List[Dict], bank_df: pd.DataFrame) -> str:
        """
        Determine severity level based on review sentiment and ratings.
        
        Args:
            reviews: List of review dictionaries
            bank_df: DataFrame for the bank
            
        Returns:
            Severity level: 'High', 'Medium', or 'Low'
        """
        if not reviews:
            return 'Low'
        
        # Count negative reviews in this theme
        negative_count = sum(1 for r in reviews if r.get('sentiment') == 'Negative')
        negative_pct = (negative_count / len(reviews)) * 100
        
        # Count low ratings (1-2) in this theme
        low_rating_count = sum(1 for r in reviews if isinstance(r.get('rating'), (int, float)) and r.get('rating', 5) <= 2)
        low_rating_pct = (low_rating_count / len(reviews)) * 100
        
        # Determine severity
        if negative_pct >= 70 or low_rating_pct >= 70:
            return 'High'
        elif negative_pct >= 40 or low_rating_pct >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def _extract_supporting_keywords(self, theme_name: str, reviews: List[Dict]) -> List[str]:
        """
        Extract keywords that support a theme from reviews.
        
        Args:
            theme_name: Name of the theme
            reviews: List of review dictionaries
            
        Returns:
            List of supporting keywords
        """
        if theme_name not in self.THEME_KEYWORDS:
            return []
        
        theme_keywords = self.THEME_KEYWORDS[theme_name]['keywords']
        found_keywords = []
        
        for review in reviews:
            text = review.get('review_text', '').lower()
            for keyword in theme_keywords:
                if keyword in text and keyword not in found_keywords:
                    found_keywords.append(keyword)
        
        return found_keywords[:10]  # Return top 10

