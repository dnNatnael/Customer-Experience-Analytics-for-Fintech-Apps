# Database Directory

This directory contains all database-related files for Task 3.

## Files

### `schema.sql`
Complete SQL schema definition including:
- `banks` table with bank_id, bank_name, app_name
- `reviews` table with all required columns
- Foreign key constraints with ON DELETE CASCADE
- CHECK constraints for data validation
- Indexes for performance optimization
- Table and column comments for documentation

### `sample_queries.sql`
Comprehensive collection of SQL queries for:
- Data integrity verification
- Sentiment analysis queries
- Rating analysis queries
- Temporal analysis queries
- Data quality checks
- Summary statistics

## Usage

### Create Database Schema

```bash
psql -U postgres -d bank_reviews -f database/schema.sql
```

### Run Sample Queries

```bash
psql -U postgres -d bank_reviews
```

Then copy and paste queries from `sample_queries.sql`.

## Exported Files

After running `scripts/export_schema.py`, you may find:
- `exported_schema.sql` - Schema-only export
- `bank_reviews_full_dump.sql` - Full database export (schema + data)

## Related Scripts

- `scripts/setup_database.py` - Automated database setup and data insertion
- `scripts/validate_database.py` - Database validation and reporting
- `scripts/export_schema.py` - Schema export utility

