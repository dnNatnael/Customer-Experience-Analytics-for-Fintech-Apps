-- ============================================================================
-- Sample SQL Queries for Data Validation and Analysis
-- Database: bank_reviews
-- ============================================================================

-- ============================================================================
-- 1. DATA INTEGRITY QUERIES
-- ============================================================================

-- 1.1 Total number of reviews per bank
SELECT 
    b.bank_name,
    b.app_name,
    COUNT(r.review_id) AS total_reviews
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name, b.app_name
ORDER BY total_reviews DESC;

-- 1.2 Average rating per bank
SELECT 
    b.bank_name,
    ROUND(AVG(r.rating)::numeric, 2) AS average_rating,
    COUNT(r.review_id) AS review_count,
    MIN(r.rating) AS min_rating,
    MAX(r.rating) AS max_rating
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name
ORDER BY average_rating DESC;

-- 1.3 Verify foreign key constraints (should return 0 rows)
SELECT 
    r.review_id,
    r.bank_id,
    r.review_text
FROM reviews r
WHERE r.bank_id NOT IN (SELECT bank_id FROM banks);

-- 1.4 Check for null values in critical columns
SELECT 
    COUNT(*) AS total_reviews,
    COUNT(review_text) AS reviews_with_text,
    COUNT(rating) AS reviews_with_rating,
    COUNT(sentiment_label) AS reviews_with_sentiment,
    COUNT(sentiment_score) AS reviews_with_sentiment_score,
    COUNT(review_date) AS reviews_with_date,
    COUNT(source) AS reviews_with_source
FROM reviews;

-- 1.5 Check rating range validity (should all be between 1 and 5)
SELECT 
    rating,
    COUNT(*) AS count
FROM reviews
GROUP BY rating
ORDER BY rating;

-- 1.6 Check sentiment_score range validity (should be between 0 and 1)
SELECT 
    MIN(sentiment_score) AS min_score,
    MAX(sentiment_score) AS max_score,
    AVG(sentiment_score) AS avg_score
FROM reviews
WHERE sentiment_score IS NOT NULL;

-- ============================================================================
-- 2. SENTIMENT ANALYSIS QUERIES
-- ============================================================================

-- 2.1 Sentiment distribution per bank
SELECT 
    b.bank_name,
    r.sentiment_label,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY b.bank_name), 2) AS percentage
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name, r.sentiment_label
ORDER BY b.bank_name, count DESC;

-- 2.2 Average sentiment score per bank
SELECT 
    b.bank_name,
    ROUND(AVG(r.sentiment_score)::numeric, 4) AS avg_sentiment_score,
    COUNT(*) AS review_count
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
WHERE r.sentiment_score IS NOT NULL
GROUP BY b.bank_name
ORDER BY avg_sentiment_score DESC;

-- 2.3 Reviews with highest and lowest sentiment scores
SELECT 
    b.bank_name,
    r.review_text,
    r.rating,
    r.sentiment_label,
    r.sentiment_score
FROM reviews r
JOIN banks b ON r.bank_id = b.bank_id
WHERE r.sentiment_score IS NOT NULL
ORDER BY r.sentiment_score DESC
LIMIT 10;

SELECT 
    b.bank_name,
    r.review_text,
    r.rating,
    r.sentiment_label,
    r.sentiment_score
FROM reviews r
JOIN banks b ON r.bank_id = b.bank_id
WHERE r.sentiment_score IS NOT NULL
ORDER BY r.sentiment_score ASC
LIMIT 10;

-- ============================================================================
-- 3. RATING ANALYSIS QUERIES
-- ============================================================================

-- 3.1 Rating distribution per bank
SELECT 
    b.bank_name,
    r.rating,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY b.bank_name), 2) AS percentage
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name, r.rating
ORDER BY b.bank_name, r.rating DESC;

-- 3.2 Reviews by rating category (High: 4-5, Medium: 3, Low: 1-2)
SELECT 
    b.bank_name,
    CASE 
        WHEN r.rating >= 4 THEN 'High (4-5)'
        WHEN r.rating = 3 THEN 'Medium (3)'
        WHEN r.rating <= 2 THEN 'Low (1-2)'
    END AS rating_category,
    COUNT(*) AS count
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_name, rating_category
ORDER BY b.bank_name, rating_category;

-- ============================================================================
-- 4. TEMPORAL ANALYSIS QUERIES
-- ============================================================================

-- 4.1 Reviews by month
SELECT 
    DATE_TRUNC('month', review_date) AS month,
    COUNT(*) AS review_count
FROM reviews
WHERE review_date IS NOT NULL
GROUP BY month
ORDER BY month DESC;

-- 4.2 Reviews per bank by year
SELECT 
    b.bank_name,
    EXTRACT(YEAR FROM r.review_date) AS year,
    COUNT(*) AS review_count
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
WHERE r.review_date IS NOT NULL
GROUP BY b.bank_name, year
ORDER BY b.bank_name, year DESC;

-- ============================================================================
-- 5. DATA QUALITY QUERIES
-- ============================================================================

-- 5.1 Reviews with missing critical data
SELECT 
    review_id,
    bank_id,
    CASE WHEN review_text IS NULL THEN 'Missing Text' END AS missing_text,
    CASE WHEN rating IS NULL THEN 'Missing Rating' END AS missing_rating,
    CASE WHEN sentiment_label IS NULL THEN 'Missing Sentiment' END AS missing_sentiment
FROM reviews
WHERE review_text IS NULL 
   OR rating IS NULL 
   OR sentiment_label IS NULL;

-- 5.2 Duplicate review text check
SELECT 
    review_text,
    COUNT(*) AS occurrence_count,
    STRING_AGG(bank_id::text, ', ') AS bank_ids
FROM reviews
WHERE review_text IS NOT NULL
GROUP BY review_text
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC
LIMIT 20;

-- 5.3 Review text length statistics
SELECT 
    b.bank_name,
    AVG(LENGTH(r.review_text)) AS avg_text_length,
    MIN(LENGTH(r.review_text)) AS min_text_length,
    MAX(LENGTH(r.review_text)) AS max_text_length
FROM banks b
JOIN reviews r ON b.bank_id = r.bank_id
WHERE r.review_text IS NOT NULL
GROUP BY b.bank_name;

-- ============================================================================
-- 6. SUMMARY STATISTICS
-- ============================================================================

-- 6.1 Overall database summary
SELECT 
    (SELECT COUNT(*) FROM banks) AS total_banks,
    (SELECT COUNT(*) FROM reviews) AS total_reviews,
    (SELECT ROUND(AVG(rating)::numeric, 2) FROM reviews WHERE rating IS NOT NULL) AS overall_avg_rating,
    (SELECT COUNT(DISTINCT bank_id) FROM reviews) AS banks_with_reviews;

-- 6.2 Complete bank summary with all metrics
SELECT 
    b.bank_name,
    b.app_name,
    COUNT(r.review_id) AS total_reviews,
    ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
    ROUND(AVG(r.sentiment_score)::numeric, 4) AS avg_sentiment_score,
    COUNT(CASE WHEN r.sentiment_label = 'Positive' THEN 1 END) AS positive_reviews,
    COUNT(CASE WHEN r.sentiment_label = 'Negative' THEN 1 END) AS negative_reviews,
    COUNT(CASE WHEN r.sentiment_label = 'Neutral' THEN 1 END) AS neutral_reviews,
    MIN(r.review_date) AS earliest_review,
    MAX(r.review_date) AS latest_review
FROM banks b
LEFT JOIN reviews r ON b.bank_id = r.bank_id
GROUP BY b.bank_id, b.bank_name, b.app_name
ORDER BY total_reviews DESC;

