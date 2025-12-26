# Review Trend Analysis System

A smart tool that analyzes Google Play Store reviews and generates trend reports. Think of it as your automated feedback analyzer that actually understands what customers are saying.

## What Does This Do?

This project helps you make sense of app reviews by:
- Scraping reviews from Google Play Store
- Processing them day by day
- Figuring out what topics people are talking about
- Grouping similar complaints/feedback together (because "delivery guy was rude" and "delivery partner impolite" are basically the same thing)
- Showing you trends over time

## Why This Approach?

Instead of traditional topic modeling (LDA, TopicBERT, etc), I went with modern LLMs because:

1. **Better Topic Extraction**: Actually understands context, not just keyword matching
2. **Smart Consolidation**: Automatically groups "app crashes", "app freezing", "app not working" into one topic
3. **No Training Required**: Works out of the box without needing training data

### Trend Tracking

- Processes reviews day by day
- Shows you trends for the last 30 days
- Exports to CSV, JSON, Excel - whatever you need

### Cool Features

- Deduplicates topics automatically (no more "delivery late" vs "late delivery" nonsense)
- Learns new topics as they emerge
- Handles API failures gracefully with retry logic
- Can resume processing if something breaks

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

## Getting Started

You'll need:
- Python 3.8 or higher
- An OpenAI API key (get one at platform.openai.com)

### Setup

1. Clone this repo:
```bash
git clone <repository-url>
cd review-trend-agent
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
```bash
cp .env.example .env
```

Edit the `.env` file and add your API key:
```
OPENAI_API_KEY=your_api_key_here
APP_PACKAGE_NAME=com.application.zomato
START_DATE=2024-06-01
```

## Usage

### Quick Start

Just run this to analyze Zomato reviews:

```bash
python main.py --package com.application.zomato
```

### All the Options

```bash
python main.py [OPTIONS]

Options:
  --package TEXT          App package name (e.g., com.application.zomato)
  --start-date TEXT       Start date YYYY-MM-DD
  --end-date TEXT         End date YYYY-MM-DD
  --target-date TEXT      Target date for report
  --scrape-only           Just scrape, don't process
  --process-only          Just process existing data
  --report-only           Just generate reports from saved data
```

### Examples

**Analyze Swiggy app:**
```bash
python main.py \
  --package in.swiggy.android \
  --start-date 2024-06-01 \
  --end-date 2024-12-25
```

**Already have the data? Just process it:**
```bash
python main.py --process-only --target-date 2024-12-25
```

**Regenerate a report without reprocessing everything:**
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

## The Main Problem This Solves

Without consolidation, you get fragmented data:
```
❌ Before:
- "Delivery guy rude" (23 mentions)
- "Delivery partner impolite" (15 mentions)
- "Delivery person bad behavior" (18 mentions)

✅ After:
- "Delivery partner rude" (56 mentions)
```

This makes a huge difference when you're trying to spot trends. Instead of three small spikes, you see one clear pattern.

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

Just being honest about what this doesn't do:

1. Needs OpenAI API access (costs money, but not much - around $1-2 per 1000 reviews)
2. Subject to API rate limits
3. Only works well with English reviews right now
4. Processes in batches, not real-time

## What Could Be Added

Some ideas for future improvements:
- Apple App Store support (currently only Google Play)
- Multi-language support
- A web dashboard for visualization
- Real-time streaming instead of batch processing
- Anomaly detection (alert when a topic suddenly spikes)

## License

MIT License

## Contact

For questions or issues, please create an issue in the GitHub repository.
