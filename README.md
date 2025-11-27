# Customer Experience Analytics for Fintech Apps

A comprehensive analytics project for analyzing customer reviews of Ethiopian banking mobile applications from the Google Play Store.

## Project Overview

This project collects, analyzes, and provides insights on customer reviews for three major Ethiopian banking apps:
- **Commercial Bank of Ethiopia (CBE)** - Mobile Banking App
- **Bank of Abyssinia (BOA)** - Mobile Banking App  
- **Dashen Bank** - Amole App

The project is organized into multiple tasks focusing on data collection, sentiment analysis, thematic analysis, database engineering, and actionable insights.

---

## 📁 Project Structure

```
Customer-Experience-Analytics-for-Fintech-Apps/
│
├── data/
│   ├── raw/              # Raw scraped data
│   ├── cleaned/          # Cleaned datasets
│   └── processed/        # Processed data for analysis
│
├── scripts/              # Python scripts for data processing
│   └── scrape_reviews.py # Main scraping script for Task 1
│
├── notebooks/            # Jupyter notebooks for interactive analysis
│   └── task1_data_collection.ipynb
│
├── src/                  # Source code modules
│
├── reports/              # Analysis reports
│   ├── task1_data_collection.md
│   ├── task2_sentiment_theme.md
│   ├── task3_database_engineering.md
│   └── task4_insights_recommendations.md
│
├── tests/                # Unit tests
│
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Customer-Experience-Analytics-for-Fintech-Apps
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📊 Task 1: Data Collection and Preprocessing

### Overview

Task 1 involves scraping Google Play Store reviews for three Ethiopian banking apps, cleaning and preprocessing the data, and creating a structured dataset.

### Objectives

✅ Scrape a minimum of 400 reviews per bank (1,200+ total)  
✅ Clean and preprocess the collected reviews  
✅ Save the final structured dataset as `clean_reviews.csv`  
✅ Maintain clean, organized project code  

### Target Apps

| Bank | App Name | App ID |
|------|----------|--------|
| CBE | Commercial Bank of Ethiopia | `com.combanketh.mobilebanking` |
| BOA | Bank of Abyssinia | `com.boa.boaMobileBanking` |
| Dashen | Dashen Bank (Amole App) | `com.cr2.amolelight` |

### Usage

#### Option 1: Run Python Script

```bash
python scripts/scrape_reviews.py
```

This script will:
- Scrape reviews from Google Play Store for all three apps
- Clean and preprocess the data
- Remove duplicates and invalid records
- Save the cleaned dataset to `data/cleaned/clean_reviews.csv`
- Display summary statistics and KPI checks

#### Option 2: Use Jupyter Notebook

```bash
jupyter notebook notebooks/task1_data_collection.ipynb
```

Open and run the cells interactively for step-by-step execution.

### Output

The script generates:
- **`data/cleaned/clean_reviews.csv`** - Cleaned dataset with the following columns:
  - `review_text`: The review content
  - `rating`: Rating score (1-5)
  - `date`: Review date (YYYY-MM-DD format)
  - `bank`: Bank name
  - `source`: Always "Google Play"

### Current Dataset Statistics

- **Total Reviews:** 1,343 (✅ exceeds target of 1,200+)
- **Reviews by Bank:**
  - Bank of Abyssinia: 491 (✅ exceeds 400)
  - Commercial Bank of Ethiopia: 477 (✅ exceeds 400)
  - Dashen Bank: 375 (slightly below 400, but maximum available)
- **Missing Data:** 0.00% (✅ exceeds <5% target)
- **Date Range:** 2022-07-16 to 2025-11-26

### Key Features

- **Automatic Deduplication:** Removes duplicate reviews within and across banks
- **Data Validation:** Ensures all reviews have complete information
- **Progress Tracking:** Real-time progress bars using `tqdm`
- **Error Handling:** Robust error handling for network issues
- **Rate Limiting:** Built-in delays to avoid API throttling

### Challenges Encountered

1. **Duplicate Reviews:** Google Play Store returns duplicate reviews across API calls
   - **Solution:** Implemented deduplication at both bank-level and dataset-level

2. **Limited Reviews for Dashen Bank:** Only 503 total reviews available
   - **Solution:** Scraped all available reviews; 375 unique reviews retained after deduplication

3. **API Rate Limiting:** Risk of being throttled
   - **Solution:** Implemented 0.5-second delays between API calls

### Deliverables

- ✅ `scripts/scrape_reviews.py` - Scraping and preprocessing script
- ✅ `notebooks/task1_data_collection.ipynb` - Interactive notebook
- ✅ `data/cleaned/clean_reviews.csv` - Cleaned dataset (1,343 reviews)
- ✅ `reports/task1_data_collection.md` - Comprehensive report

---

## 📈 Key Performance Indicators (KPIs)

### Task 1 KPIs

| KPI | Target | Achieved | Status |
|-----|--------|----------|--------|
| Total Reviews | 1,200+ | 1,343 | ✅ **PASS** |
| Reviews per Bank | 400+ | CBE: 477, BOA: 491, Dashen: 375 | ⚠️ **PARTIAL** |
| Missing Data | <5% | 0.00% | ✅ **PASS** |
| Clean Codebase | Required | ✅ | ✅ **PASS** |
| Documentation | Required | ✅ | ✅ **PASS** |

**Note:** Dashen Bank has 375 reviews (6.3% below target) because only 503 total reviews were available. After deduplication, 375 unique reviews remained, representing the maximum available data for this app.

---

## 📝 Requirements

Key dependencies for Task 1:

- `google-play-scraper` - For scraping Google Play Store reviews
- `pandas` - For data manipulation and analysis
- `numpy` - For numerical operations
- `tqdm` - For progress bars

See `requirements.txt` for complete list of dependencies.

---

## 🔧 Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_task1.py
```

### Code Style

This project follows PEP 8 Python style guidelines. Consider using:
- `black` for code formatting
- `flake8` or `pylint` for linting

---

## 📚 Documentation

- **Task 1 Report:** See `reports/task1_data_collection.md` for detailed documentation
- **Code Comments:** All scripts include inline documentation
- **Notebooks:** Jupyter notebooks include markdown explanations

---

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## 📄 License

[Add your license information here]

---

## 👥 Authors

[Add author information here]

---

## 🙏 Acknowledgments

- Google Play Store for providing review data
- Ethiopian banking institutions (CBE, BOA, Dashen) for their mobile banking applications

---

**Last Updated:** 2025-01-27  
**Current Task:** Task 1 - Data Collection and Preprocessing ✅  
**Next Task:** Task 2 - Sentiment and Thematic Analysis