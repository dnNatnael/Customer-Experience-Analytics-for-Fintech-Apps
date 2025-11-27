"""
Sentiment Analysis Module

This module performs sentiment analysis using multiple models:
1. distilbert-base-uncased-finetuned-sst-2-english (primary)
2. VADER (fallback/comparison)
3. TextBlob (fallback/comparison)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Try to import transformers for DistilBERT
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers library not available. Will use VADER and TextBlob only.")

# VADER Sentiment
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("Warning: vaderSentiment not available.")

# TextBlob
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: textblob not available.")


class SentimentAnalyzer:
    """Sentiment analysis using multiple models."""
    
    def __init__(self):
        """Initialize sentiment analyzers."""
        self.distilbert_pipeline = None
        self.vader_analyzer = None
        
        # Initialize DistilBERT (primary)
        if TRANSFORMERS_AVAILABLE:
            try:
                print("Loading DistilBERT model...")
                self.distilbert_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1  # Use CPU
                )
                print("DistilBERT model loaded successfully.")
            except Exception as e:
                print(f"Warning: Could not load DistilBERT: {e}")
                self.distilbert_pipeline = None
        
        # Initialize VADER
        if VADER_AVAILABLE:
            self.vader_analyzer = SentimentIntensityAnalyzer()
    
    def analyze_with_distilbert(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Analyze sentiment using DistilBERT.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (label, score) or None if unavailable
        """
        if not self.distilbert_pipeline or not text or pd.isna(text):
            return None
        
        try:
            # Truncate very long texts (DistilBERT has token limit)
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            result = self.distilbert_pipeline(text)[0]
            label = result['label']
            score = result['score']
            
            # Normalize label to Positive/Negative
            if label == 'POSITIVE':
                return ('Positive', score)
            elif label == 'NEGATIVE':
                return ('Negative', 1 - score)  # Invert score for negative
            else:
                return ('Neutral', 0.5)
        except Exception as e:
            print(f"Error in DistilBERT analysis: {e}")
            return None
    
    def analyze_with_vader(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Analyze sentiment using VADER.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (label, score) or None if unavailable
        """
        if not self.vader_analyzer or not text or pd.isna(text):
            return None
        
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            compound = scores['compound']
            
            if compound >= 0.05:
                label = 'Positive'
                score = (compound + 1) / 2  # Normalize to 0-1
            elif compound <= -0.05:
                label = 'Negative'
                score = (abs(compound) + 1) / 2  # Normalize to 0-1
            else:
                label = 'Neutral'
                score = 0.5
            
            return (label, score)
        except Exception as e:
            print(f"Error in VADER analysis: {e}")
            return None
    
    def analyze_with_textblob(self, text: str) -> Optional[Tuple[str, float]]:
        """
        Analyze sentiment using TextBlob.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (label, score) or None if unavailable
        """
        if not TEXTBLOB_AVAILABLE or not text or pd.isna(text):
            return None
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                label = 'Positive'
                score = (polarity + 1) / 2  # Normalize to 0-1
            elif polarity < -0.1:
                label = 'Negative'
                score = (abs(polarity) + 1) / 2  # Normalize to 0-1
            else:
                label = 'Neutral'
                score = 0.5
            
            return (label, score)
        except Exception as e:
            print(f"Error in TextBlob analysis: {e}")
            return None
    
    def analyze(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment using the best available model (priority: DistilBERT > VADER > TextBlob).
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (sentiment_label, sentiment_score)
        """
        # Try DistilBERT first
        result = self.analyze_with_distilbert(text)
        if result:
            return result
        
        # Fallback to VADER
        result = self.analyze_with_vader(text)
        if result:
            return result
        
        # Fallback to TextBlob
        result = self.analyze_with_textblob(text)
        if result:
            return result
        
        # Default if all fail
        return ('Neutral', 0.5)
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'review_text') -> pd.DataFrame:
        """
        Analyze sentiment for all texts in a DataFrame.
        
        Args:
            df: Input DataFrame
            text_column: Name of the column containing text
            
        Returns:
            DataFrame with 'sentiment_label' and 'sentiment_score' columns
        """
        df = df.copy()
        
        print("Analyzing sentiment for all reviews...")
        results = df[text_column].apply(self.analyze)
        
        df['sentiment_label'] = results.apply(lambda x: x[0])
        df['sentiment_score'] = results.apply(lambda x: x[1])
        
        return df
    
    def compare_with_rating(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compare sentiment with ratings to identify anomalies.
        
        Args:
            df: DataFrame with sentiment_label, sentiment_score, and rating columns
            
        Returns:
            DataFrame with 'sentiment_rating_match' column
        """
        df = df.copy()
        
        def is_match(row):
            rating = row['rating']
            sentiment = row['sentiment_label']
            
            # High rating (4-5) should be positive
            if rating >= 4 and sentiment == 'Positive':
                return 'Match'
            # Low rating (1-2) should be negative
            elif rating <= 2 and sentiment == 'Negative':
                return 'Match'
            # Medium rating (3) can be neutral or mixed
            elif rating == 3:
                return 'Neutral'
            # Mismatch cases
            else:
                return 'Mismatch'
        
        df['sentiment_rating_match'] = df.apply(is_match, axis=1)
        return df

