# Getting Started

Quick setup guide for the Review Trend Analysis System.

## Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- An OpenAI API key (for GPT-4 access)
- Internet connection (for scraping and API calls)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd review-trend-agent
pip install -r requirements.txt
```

Optional: Use a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```bash
# Required
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional - customize these
APP_PACKAGE_NAME=com.application.zomato
START_DATE=2024-06-01
```

**Where to get an OpenAI API key:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env`

### 3. Run the Demo

Test the system with sample data (no API key needed for demo):
```bash
python examples/quick_start.py
```

This will demonstrate:
- Topic extraction
- Topic consolidation
- Trend report generation

### 4. Run with Real Data

#### For Zomato:
```bash
python main.py --package com.application.zomato --start-date 2024-06-01
```

#### For Swiggy:
```bash
python main.py --package in.swiggy.android --start-date 2024-06-01
```

#### For any other app:
```bash
# Find package name from Play Store URL
# Example: https://play.google.com/store/apps/details?id=com.example.app
python main.py --package com.example.app --start-date 2024-06-01
```

## Understanding the Output

After running, you'll find reports in the `output/` directory:

```
output/
├── trend_report_2024-12-25.csv        # CSV format (open in Excel)
├── trend_report_2024-12-25.json       # JSON format (for APIs)
├── trend_report_2024-12-25.xlsx       # Excel format (with formatting)
├── summary_2024-12-25.json            # Summary statistics
└── processor_state.json               # System state (for resuming)
```

### Sample Report Structure

```
Topic                    Jun 1  Jun 2  Jun 3  ...  Total  Trend
Delivery delay              12      8     15  ...    450  +15.3%
Food arrived cold            5      7      3  ...    220   -8.2%
Delivery partner rude        8     12      6  ...    185  +22.1%
```

## Common Use Cases

### 1. Analyze Reviews for a Specific Month

```bash
python main.py \
  --package com.application.zomato \
  --start-date 2024-06-01 \
  --end-date 2024-06-30 \
  --target-date 2024-06-30
```

### 2. Update Analysis with New Reviews

```bash
# First run - scrape and process
python main.py --package com.application.zomato

# Later - process new reviews only
python main.py --package com.application.zomato --start-date 2024-12-20
```

### 3. Regenerate Report for Different Date

```bash
# Generate report for a specific date without reprocessing
python main.py --report-only --target-date 2024-06-15
```

### 4. Process Existing Batches

```bash
# Skip scraping, just process data you already have
python main.py --process-only --target-date 2024-12-25
```

## Advanced Configuration

### Customize Seed Topics

Edit `config/config.py`:

```python
SEED_TOPICS = [
    "Your custom topic 1",
    "Your custom topic 2",
    # ... add more
]
```

### Adjust Model Selection

For cost optimization, configure models in `.env`:

```bash
# Use different models for different tasks
TOPIC_EXTRACTION_MODEL=gpt-3.5-turbo
TOPIC_CONSOLIDATION_MODEL=gpt-4-turbo-preview
```

### Adjust Processing Parameters

In `.env`:
```bash
TEMPERATURE=0.3          # Lower = more deterministic (0.0-1.0)
MAX_RETRIES=3           # Number of retries on API failure
```

## Troubleshooting

### Issue: "OpenAI API key not found"

**Solution**: Make sure you've created `.env` and added your API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "No reviews found"

**Possible causes**:
1. Invalid package name
2. Date range too restrictive
3. App has no reviews in that period

**Solution**: Check the package name and expand date range:
```bash
python main.py --package com.application.zomato --start-date 2024-01-01
```

### Issue: "Rate limit exceeded"

**Solution**: The OpenAI API has rate limits. Wait a few minutes or:
1. Reduce batch size in code
2. Add delays between batches
3. Upgrade your OpenAI plan

### Issue: "JSON decode error"

**Solution**: API occasionally returns invalid responses. The system will:
1. Automatically retry (up to MAX_RETRIES times)
2. Skip failed batches if retry fails
3. Continue processing remaining data

Check logs for details.

### Issue: Package installation fails

**Solution**:
```bash
# Upgrade pip first
pip install --upgrade pip

# Install packages one by one to identify issues
pip install openai
pip install google-play-scraper
# etc.
```

## API Cost Estimation

Approximate costs using OpenAI API:
- Topic extraction: ~$0.01 per 10 reviews
- Topic consolidation: ~$0.005 per 100 topics

**Examples**:
- 100 reviews: ~$0.10
- 1,000 reviews: ~$1.00
- 10,000 reviews: ~$10.00

**Optimization tips**:
1. Use cost-effective models for bulk processing
2. Increase batch sizes
3. Leverage cached results

## Next Steps

1. **Run on your target app**: Choose Swiggy/Zomato/other
2. **Analyze results**: Check output reports
3. **Customize**: Adjust seed topics for your domain
4. **Automate**: Set up daily/weekly cron jobs
5. **Integrate**: Use JSON output in your dashboards

## Support

If you encounter issues:

1. Check this guide first
2. Review `ARCHITECTURE.md` for technical details
3. Run the demo: `python examples/quick_start.py`
4. Check GitHub issues
5. Review error logs

## Performance Tips

### For Large Datasets (10K+ reviews)

1. **Process in stages**:
   ```bash
   # Month 1
   python main.py --start-date 2024-06-01 --end-date 2024-06-30

   # Month 2
   python main.py --start-date 2024-07-01 --end-date 2024-07-31
   ```

2. **Use processor state**:
   - First run creates `processor_state.json`
   - Subsequent runs load existing taxonomy
   - Faster processing, consistent results

3. **Increase batch size**:
   Edit agents to process more reviews per API call (trade accuracy for speed)

### For Multiple Apps

Create separate config files:
```bash
# Zomato
APP_PACKAGE_NAME=com.application.zomato python main.py

# Swiggy
APP_PACKAGE_NAME=in.swiggy.android python main.py
```

## Sample Workflow

```bash
# 1. Initial setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key

# 2. Test with demo
python examples/quick_start.py

# 3. Run on real data
python main.py --package com.application.zomato --start-date 2024-06-01

# 4. Check results
ls -l output/
open output/trend_report_*.csv

# 5. Generate report for specific date
python main.py --report-only --target-date 2024-06-15
```

---

**Ready to start? Run the quick start demo:**
```bash
python examples/quick_start.py
```
