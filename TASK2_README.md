# Task 2: Sentiment & Thematic Analysis - README

## Overview

This task performs comprehensive sentiment analysis and thematic analysis on Google Play Store reviews for three Ethiopian banking apps:
- Commercial Bank of Ethiopia (CBE)
- Bank of Abyssinia (BOA)
- Dashen Bank

## Approach

### 1. Modular Code Structure

The analysis is implemented using a modular architecture with separate modules for each component:

- **`src/text_preprocessor.py`**: NLP preprocessing pipeline (lowercasing, tokenization, stopword removal, lemmatization)
- **`src/sentiment_analyzer.py`**: Sentiment analysis using multiple models (DistilBERT, VADER, TextBlob)
- **`src/keyword_extractor.py`**: Keyword and N-gram extraction using TF-IDF and spaCy
- **`src/theme_analyzer.py`**: Thematic analysis to group keywords into actionable themes

### 2. Sentiment Analysis

**Primary Model**: DistilBERT (distilbert-base-uncased-finetuned-sst-2-english)
- Fast and accurate sentiment classification
- Returns both label (Positive/Negative/Neutral) and confidence score (0-1)

**Fallback Models**:
- VADER: Rule-based sentiment analyzer for social media text
- TextBlob: Simple polarity-based sentiment analysis

### 3. NLP Preprocessing

All reviews undergo:
- Lowercasing
- Tokenization (spaCy)
- Stop-word removal
- Lemmatization
- Bigram and trigram phrase detection

### 4. Keyword Extraction

- **TF-IDF**: Extracts 1- to 3-grams with importance scoring
- **spaCy Noun Chunks**: Identifies meaningful phrases
- Separate extraction for:
  - Overall keywords per bank
  - Complaint keywords (from negative reviews)
  - Praise keywords (from positive reviews)

### 5. Thematic Analysis

Keywords are mapped to 8 predefined theme categories:
- Account Access Issues
- Transaction Performance
- Stability & Reliability
- User Interface & Experience
- Customer Support
- Feature Requests
- Security Concerns
- Network & Connectivity

Each theme includes:
- Frequency count
- Severity assessment (High/Medium/Low)
- Supporting keywords
- Representative reviews

## Results

### Dataset Statistics
- **Total Reviews Analyzed**: 957
- **Sentiment Coverage**: 100% (all reviews scored)
- **Banks**: 3 (CBE: 325, BOA: 333, Dashen: 299)

### Global Sentiment Distribution
- **Positive**: 42.84% (410 reviews)
- **Neutral**: 46.19% (442 reviews)
- **Negative**: 10.97% (105 reviews)
- **Mean Sentiment Score**: 0.6439

### Top Themes Across All Banks
1. Stability & Reliability: 140 reviews (14.63%)
2. User Interface & Experience: 113 reviews (11.81%)
3. Transaction Performance: 95 reviews (9.93%)
4. Feature Requests: 88 reviews (9.20%)
5. Customer Support: 55 reviews (5.75%)

### Per-Bank Highlights

**Commercial Bank of Ethiopia**:
- Highest positive sentiment (45.54%)
- Lowest negative sentiment (6.15%)
- Top theme: Stability & Reliability (10.2%)

**Bank of Abyssinia**:
- Highest negative sentiment (15.92%)
- Highest 1-star rating percentage (39.64%)
- Top theme: Stability & Reliability (20.4%) - **High Severity**

**Dashen Bank**:
- Highest mean sentiment score (0.6500)
- Top theme: User Interface & Experience (17.4%)

## Key Findings

1. **Polarized Ratings**: 55.69% 5-star vs 25.39% 1-star reviews indicates strong opinions
2. **Stability Issues**: Most common theme across all banks, especially critical for BOA
3. **Sentiment-Rating Anomalies**: 5.75% of reviews show mismatched sentiment and ratings
4. **Bank of Abyssinia**: Requires immediate attention for stability and reliability issues

## Output Files

1. **`data/processed/sentiment_analysis_results.csv`**
   - Contains all required columns: review_id, bank_name, review_text, rating, sentiment_label, sentiment_score, identified_theme(s), keywords
   - 957 rows of analyzed data

2. **`reports/task2_sentiment_theme.md`**
   - Comprehensive markdown report with:
     - Global analysis summary
     - Per-bank detailed analysis
     - Theme breakdowns with representative reviews
     - Actionable recommendations
     - Methodology documentation

## Usage

### Run Analysis
```bash
python scripts/sentiment_analysis.py
```

### Generate Report
```bash
python scripts/generate_report.py
```

## KPI Verification

✅ **Sentiment computed for 100% of reviews** (Target: 90%+)  
✅ **Minimum 400 reviews**: 957 reviews analyzed  
✅ **At least 2 themes per bank**: All banks have 5 themes identified  
✅ **Modular code structure**: Separate modules for each component  
✅ **Clear mapping logic**: Keywords mapped to themes with documented logic  

## Dependencies

- transformers (for DistilBERT)
- vaderSentiment
- textblob
- spacy (with en_core_web_sm model)
- scikit-learn (for TF-IDF)
- pandas, numpy

## Notes

- The analysis handles multilingual content (English and Amharic)
- Short reviews may have limited keyword extraction (expected behavior)
- Theme identification uses pattern matching and keyword mapping
- Severity assessment based on sentiment and rating distribution within themes

