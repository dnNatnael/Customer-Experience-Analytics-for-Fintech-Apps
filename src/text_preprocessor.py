"""
NLP Preprocessing Pipeline Module

This module handles text preprocessing including:
- Lowercasing
- Tokenization
- Stop-word removal
- Lemmatization
- Optional: bigram and trigram phrase detection
"""

import re
import spacy
from typing import List, Tuple
import pandas as pd
from collections import Counter

# Load spaCy model (English)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy English model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None


class TextPreprocessor:
    """Text preprocessing pipeline for review analysis."""
    
    def __init__(self, remove_stopwords: bool = True, lemmatize: bool = True):
        """
        Initialize the text preprocessor.
        
        Args:
            remove_stopwords: Whether to remove stop words
            lemmatize: Whether to lemmatize tokens
        """
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        self.nlp = nlp
        
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess a single text string.
        
        Args:
            text: Input text string
            
        Returns:
            Cleaned and preprocessed text
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        if not self.nlp:
            return text
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract tokens
        tokens = []
        for token in doc:
            # Skip punctuation, spaces, and special characters
            if token.is_punct or token.is_space:
                continue
            
            # Skip stop words if enabled
            if self.remove_stopwords and token.is_stop:
                continue
            
            # Lemmatize if enabled
            if self.lemmatize:
                tokens.append(token.lemma_)
            else:
                tokens.append(token.text)
        
        return ' '.join(tokens)
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str = 'review_text') -> pd.DataFrame:
        """
        Preprocess all texts in a DataFrame.
        
        Args:
            df: Input DataFrame
            text_column: Name of the column containing text
            
        Returns:
            DataFrame with new 'cleaned_text' column
        """
        df = df.copy()
        df['cleaned_text'] = df[text_column].apply(self.preprocess_text)
        return df
    
    def extract_phrases(self, text: str, n: int = 2) -> List[str]:
        """
        Extract n-gram phrases from text.
        
        Args:
            text: Input text
            n: N-gram size (2 for bigrams, 3 for trigrams)
            
        Returns:
            List of n-gram phrases
        """
        if not self.nlp:
            tokens = text.lower().split()
        else:
            doc = self.nlp(text.lower())
            tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
        
        phrases = []
        for i in range(len(tokens) - n + 1):
            phrase = ' '.join(tokens[i:i+n])
            phrases.append(phrase)
        
        return phrases
    
    def extract_noun_chunks(self, text: str) -> List[str]:
        """
        Extract noun chunks using spaCy.
        
        Args:
            text: Input text
            
        Returns:
            List of noun chunks
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        noun_chunks = [chunk.text.lower() for chunk in doc.noun_chunks]
        return noun_chunks

