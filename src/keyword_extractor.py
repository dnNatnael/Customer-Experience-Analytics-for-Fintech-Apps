"""
Keyword and N-gram Extraction Modules

This module extracts keywords and phrases using:
- TF-IDF (1- to 3-grams)
- spaCy noun-chunk extraction
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple
from collections import Counter
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None


class KeywordExtractor:
    """Extract keywords and n-grams from reviews."""
    
    def __init__(self):
        """Initialize keyword extractor."""
        self.nlp = nlp
    
    def extract_tfidf_keywords(self, texts: List[str], ngram_range: Tuple[int, int] = (1, 3), 
                               max_features: int = 100, min_df: int = 2) -> List[Tuple[str, float]]:
        """
        Extract keywords using TF-IDF.
        
        Args:
            texts: List of text strings
            ngram_range: Range of n-grams to extract (min, max)
            max_features: Maximum number of features to extract
            min_df: Minimum document frequency
            
        Returns:
            List of (keyword, tfidf_score) tuples sorted by score
        """
        if not texts:
            return []
        
        try:
            vectorizer = TfidfVectorizer(
                ngram_range=ngram_range,
                max_features=max_features,
                min_df=min_df,
                stop_words='english',
                lowercase=True
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF scores across all documents
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Create list of (keyword, score) tuples
            keywords = list(zip(feature_names, mean_scores))
            keywords.sort(key=lambda x: x[1], reverse=True)
            
            return keywords
        except Exception as e:
            print(f"Error in TF-IDF extraction: {e}")
            return []
    
    def extract_noun_chunks(self, texts: List[str]) -> List[str]:
        """
        Extract noun chunks from texts using spaCy.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of noun chunks (with frequency)
        """
        if not self.nlp:
            return []
        
        all_chunks = []
        for text in texts:
            if pd.isna(text) or not isinstance(text, str):
                continue
            
            try:
                doc = self.nlp(text)
                chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks]
                all_chunks.extend(chunks)
            except Exception as e:
                continue
        
        # Count frequencies
        chunk_counts = Counter(all_chunks)
        return chunk_counts.most_common()
    
    def extract_keywords_per_bank(self, df: pd.DataFrame, text_column: str = 'review_text',
                                  bank_column: str = 'bank', top_n: int = 50) -> Dict[str, List[Tuple[str, float]]]:
        """
        Extract top keywords for each bank.
        
        Args:
            df: DataFrame with reviews
            text_column: Name of text column
            bank_column: Name of bank column
            top_n: Number of top keywords to return per bank
            
        Returns:
            Dictionary mapping bank names to lists of (keyword, score) tuples
        """
        keywords_by_bank = {}
        
        for bank in df[bank_column].unique():
            bank_reviews = df[df[bank_column] == bank][text_column].tolist()
            keywords = self.extract_tfidf_keywords(bank_reviews, max_features=top_n)
            keywords_by_bank[bank] = keywords[:top_n]
        
        return keywords_by_bank
    
    def extract_complaint_keywords(self, df: pd.DataFrame, text_column: str = 'review_text',
                                   sentiment_column: str = 'sentiment_label', 
                                   top_n: int = 30) -> List[Tuple[str, float]]:
        """
        Extract top keywords from negative reviews.
        
        Args:
            df: DataFrame with reviews
            text_column: Name of text column
            sentiment_column: Name of sentiment label column
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        negative_reviews = df[df[sentiment_column] == 'Negative'][text_column].tolist()
        keywords = self.extract_tfidf_keywords(negative_reviews, max_features=top_n)
        return keywords[:top_n]
    
    def extract_praise_keywords(self, df: pd.DataFrame, text_column: str = 'review_text',
                                sentiment_column: str = 'sentiment_label',
                                top_n: int = 30) -> List[Tuple[str, float]]:
        """
        Extract top keywords from positive reviews.
        
        Args:
            df: DataFrame with reviews
            text_column: Name of text column
            sentiment_column: Name of sentiment label column
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        positive_reviews = df[df[sentiment_column] == 'Positive'][text_column].tolist()
        keywords = self.extract_tfidf_keywords(positive_reviews, max_features=top_n)
        return keywords[:top_n]
    
    def extract_keywords_for_review(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords for a single review.
        
        Args:
            text: Review text
            top_n: Number of keywords to return
            
        Returns:
            List of keywords
        """
        if not text or pd.isna(text):
            return []
        
        try:
            keywords = self.extract_tfidf_keywords([text], max_features=top_n, min_df=1)
            return [kw[0] for kw in keywords[:top_n]]
        except:
            # Fallback: simple word extraction for very short texts
            if self.nlp:
                try:
                    doc = self.nlp(text.lower())
                    words = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.is_alpha]
                    return list(set(words))[:top_n]
                except:
                    pass
            # Last resort: simple split
            words = [w.lower().strip() for w in text.split() if len(w) > 2]
            return list(set(words))[:top_n]

