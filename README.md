# Review Trend Analysis System

An intelligent system for analyzing Google Play Store reviews and generating trend reports using advanced natural language processing and machine learning techniques.

## Overview

This project implements an intelligent analysis system that:
- Scrapes Google Play Store reviews for any app
- Processes reviews in daily batches
- Extracts topics using natural language understanding
- Consolidates similar topics to prevent fragmentation
- Generates comprehensive trend analysis reports

## Key Features

### Advanced NLP Approach

Unlike traditional methods (LDA, TopicBERT), this system uses modern language models as intelligent processors:

1. **Topic Extraction**: Analyzes reviews and identifies issues, requests, and feedback
2. **Topic Consolidation**: Solves the duplicate topic problem by creating a unified taxonomy
3. **High Accuracy**: Ensures all relevant topics are captured and properly categorized

### Trend Analysis

- **Daily batch processing**: Treats each day's reviews as a separate batch
- **Rolling window reports**: Shows trends from T-30 to T (31 days)
- **Multiple output formats**: CSV, JSON, Excel, and text reports

### Technical Highlights

- Smart topic deduplication using semantic similarity
- Incremental taxonomy building
- Handles evolving topics over time
- Comprehensive error handling and retry logic

## Project Structure

```
review-trend-agent/
├── main.py                 # Main application entry point
├── config/
│   └── config.py          # Configuration management
├── scrapers/
│   └── play_store_scraper.py  # Google Play Store scraper
├── agents/
│   ├── topic_extraction_agent.py      # Topic extraction
│   ├── topic_consolidation_agent.py   # Topic deduplication
│   └── batch_processor.py             # Daily batch processing
├── utils/
│   └── report_generator.py   # Report generation
├── data/
│   └── daily_batches/        # Daily review batches
└── output/                   # Generated reports
```

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd review-trend-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```
OPENAI_API_KEY=your_api_key_here
APP_PACKAGE_NAME=com.application.zomato
START_DATE=2024-06-01
```

## Usage

### Quick Start

Run the complete pipeline:

```bash
python main.py --package com.application.zomato
```

### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  --package TEXT          App package name
  --start-date TEXT       Start date YYYY-MM-DD
  --end-date TEXT         End date YYYY-MM-DD
  --target-date TEXT      Target date for report (T)
  --scrape-only           Only scrape reviews
  --process-only          Only process existing batches
  --report-only           Only generate report from existing state
```

### Examples

**Analyze Swiggy reviews:**
```bash
python main.py \
  --package in.swiggy.android \
  --start-date 2024-06-01 \
  --end-date 2024-12-25
```

**Process existing data:**
```bash
python main.py --process-only --target-date 2024-12-25
```

**Generate report for specific date:**
```bash
python main.py --report-only --target-date 2024-12-25
```

## How It Works

### Step 1: Review Scraping

The scraper fetches reviews from Google Play Store and organizes them into daily batches:

```python
from scrapers.play_store_scraper import PlayStoreScraper

scraper = PlayStoreScraper("com.application.zomato")
reviews = scraper.scrape_reviews(start_date=datetime(2024, 6, 1))
batches = scraper.organize_by_date(reviews)
```

### Step 2: Topic Extraction

The extraction module processes each review using natural language understanding:

```python
from agents.topic_extraction_agent import TopicExtractionAgent

agent = TopicExtractionAgent()
extractions = agent.extract_topics(reviews)
```

**Output**:
```json
{
  "review_index": 1,
  "topics": ["Delivery delay", "Cold food"],
  "sentiment": "negative",
  "reasoning": "Customer complained about late delivery and food temperature"
}
```

### Step 3: Topic Consolidation

The consolidation module prevents duplicate topics:

**Input**:
```
- "Delivery guy was rude"
- "Delivery partner behaved badly"
- "Delivery person was impolite"
```

**Output**:
```json
{
  "canonical_name": "Delivery partner rude",
  "variants": [
    "Delivery guy was rude",
    "Delivery partner behaved badly",
    "Delivery person was impolite"
  ],
  "category": "issue"
}
```

### Step 4: Trend Report Generation

Generates a table showing topic frequency over time:

```
Topic                           Jun 1  Jun 2  Jun 3  ...  Jun 30  Total  Trend
Delivery delay                     12      8     15  ...      23    450  +15.3%
Food arrived cold                   5      7      3  ...      11    220   -8.2%
Delivery partner rude               8     12      6  ...       9    185  +22.1%
```

## Output Files

The system generates multiple output files in the `output/` directory:

- **trend_report_YYYY-MM-DD.csv**: CSV format report
- **trend_report_YYYY-MM-DD.json**: JSON format with full data
- **trend_report_YYYY-MM-DD.xlsx**: Excel report with formatting
- **summary_YYYY-MM-DD.json**: Summary statistics
- **processor_state.json**: Complete system state

## Configuration

Edit `config/config.py` or `.env` to customize:

```python
# App Configuration
APP_PACKAGE_NAME = "com.application.zomato"
START_DATE = "2024-06-01"

# Model Configuration
TOPIC_EXTRACTION_MODEL = "gpt-4-turbo-preview"
TOPIC_CONSOLIDATION_MODEL = "gpt-4-turbo-preview"
TEMPERATURE = 0.3

# Seed Topics
SEED_TOPICS = [
    "Delivery issue",
    "Food quality - stale/bad",
    "Delivery partner behavior",
    "App technical issues",
    "Payment problems",
]
```

## Seed Topics

The system includes predefined topics for food delivery apps:

- Delivery issues
- Food quality problems
- Delivery partner behavior
- App technical issues
- Payment problems
- Customer service
- Pricing and offers
- Order accuracy
- Restaurant quality
- Delivery time

New topics are automatically discovered and added as they appear in reviews.

## API Costs

Estimated costs using OpenAI API:

- Topic extraction: ~$0.01 per 10 reviews
- Topic consolidation: ~$0.005 per 100 topics
- **Total for 1000 reviews**: ~$1-2

To reduce costs:
- Use gpt-3.5-turbo instead of gpt-4-turbo-preview
- Increase batch sizes
- Cache results using processor_state.json

## Key Challenge Solved: Topic Duplication

**Problem**: Similar topics created as separate categories
```
❌ Before:
- "Delivery guy rude" (23 mentions)
- "Delivery partner impolite" (15 mentions)
- "Delivery person bad behavior" (18 mentions)

✅ After consolidation:
- "Delivery partner rude" (56 mentions)
```

**Solution**: Semantic consolidation using advanced NLP

## Sample Output

```
================================================================================
TREND ANALYSIS REPORT
Target Date: 2024-12-25
Window: T-30 to T (31 days)
================================================================================

TOP 30 TOPICS BY TOTAL MENTIONS:

Delivery delay                                     | Total:  450 | Trend:  +15.3%
App crashes/freezing                               | Total:  380 | Trend:   -5.2%
Food arrived cold                                  | Total:  320 | Trend:   +8.7%
Delivery partner rude                              | Total:  280 | Trend:  +22.1%
Order missing items                                | Total:  250 | Trend:   -2.4%
```

## Testing

Run individual components:

```bash
# Test scraper
python scrapers/play_store_scraper.py

# Test topic extraction
python agents/topic_extraction_agent.py

# Test consolidation
python agents/topic_consolidation_agent.py

# Test batch processing
python agents/batch_processor.py

# Test report generation
python utils/report_generator.py
```

## Requirements

Key dependencies:

- `openai` - OpenAI API access
- `google-play-scraper` - Play Store scraping
- `pandas` - Data processing
- `langchain` - NLP orchestration
- `tenacity` - Retry logic

See `requirements.txt` for complete list.

## Limitations

1. **API Dependency**: Requires OpenAI API access
2. **Rate Limits**: Subject to API rate limits
3. **Language**: Optimized for English reviews
4. **Processing Time**: Not real-time (batch processing)

## Future Enhancements

- Apple App Store support
- Multi-language support
- Web dashboard
- Real-time processing
- Anomaly detection

## License

MIT License

## Contact

For questions or issues, please create an issue in the GitHub repository.
