-- ============================================================================
-- PostgreSQL Database Schema for Bank Reviews
-- Database: bank_reviews
-- ============================================================================

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS banks CASCADE;

-- ============================================================================
-- Table 1: banks
-- Stores information about each banking institution
-- ============================================================================

CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name TEXT NOT NULL,
    app_name TEXT
);

-- Add unique constraint on bank_name to prevent duplicates
CREATE UNIQUE INDEX idx_banks_bank_name ON banks(bank_name);

-- ============================================================================
-- Table 2: reviews
-- Stores individual customer reviews with sentiment analysis results
-- ============================================================================

CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL,
    review_text TEXT,
    rating INTEGER,
    review_date TIMESTAMP,
    sentiment_label TEXT,
    sentiment_score FLOAT,
    source TEXT,
    -- Foreign key constraint with ON DELETE CASCADE
    CONSTRAINT fk_reviews_bank_id 
        FOREIGN KEY (bank_id) 
        REFERENCES banks(bank_id) 
        ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_reviews_bank_id ON reviews(bank_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_sentiment_label ON reviews(sentiment_label);
CREATE INDEX idx_reviews_review_date ON reviews(review_date);

-- Add check constraint for rating (should be between 1 and 5)
ALTER TABLE reviews ADD CONSTRAINT chk_rating_range 
    CHECK (rating >= 1 AND rating <= 5);

-- Add check constraint for sentiment_score (should be between 0 and 1)
ALTER TABLE reviews ADD CONSTRAINT chk_sentiment_score_range 
    CHECK (sentiment_score >= 0 AND sentiment_score <= 1);

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE banks IS 'Stores banking institution information';
COMMENT ON COLUMN banks.bank_id IS 'Primary key, auto-incrementing serial';
COMMENT ON COLUMN banks.bank_name IS 'Name of the banking institution (NOT NULL)';
COMMENT ON COLUMN banks.app_name IS 'Name of the mobile banking application';

COMMENT ON TABLE reviews IS 'Stores customer reviews with sentiment analysis';
COMMENT ON COLUMN reviews.review_id IS 'Primary key, auto-incrementing serial';
COMMENT ON COLUMN reviews.bank_id IS 'Foreign key referencing banks.bank_id';
COMMENT ON COLUMN reviews.review_text IS 'The actual review text content';
COMMENT ON COLUMN reviews.rating IS 'Rating score from 1 to 5';
COMMENT ON COLUMN reviews.review_date IS 'Timestamp when the review was posted';
COMMENT ON COLUMN reviews.sentiment_label IS 'Sentiment classification (Positive/Negative/Neutral)';
COMMENT ON COLUMN reviews.sentiment_score IS 'Sentiment confidence score (0.0 to 1.0)';
COMMENT ON COLUMN reviews.source IS 'Source of the review (e.g., Google Play)';

