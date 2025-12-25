# Output Directory

Sample reports and analysis results from the Review Trend Analysis System.

## Files in this Directory

### 1. `trend_report_2024-07-30.csv`
**Format**: CSV (Excel-compatible)
**Description**: Main trend analysis report showing topics as rows and dates as columns.

**Structure**:
- **Topic**: Name of the consolidated topic
- **Jun 30 - Jul 30**: Daily frequency counts (31 days, T-30 to T)
- **Total**: Sum of all mentions across the period
- **Trend**: Percentage change comparing last 7 days vs previous 7 days

**Use Case**: Open in Excel or Google Sheets for easy viewing and analysis.

---

### 2. `trend_report_2024-07-30.json`
**Format**: JSON
**Description**: Complete trend data in machine-readable format.

**Structure**:
```json
{
  "target_date": "2024-07-30",
  "generated_at": "ISO timestamp",
  "window_days": 31,
  "trend_data": {
    "Topic Name": {
      "2024-06-30": count,
      "2024-07-01": count,
      ...
    }
  },
  "metadata": {...}
}
```

**Use Case**: API integration, programmatic analysis, dashboards.

---

### 3. `summary_2024-07-30.json`
**Format**: JSON
**Description**: High-level summary statistics and insights.

**Contains**:
- **total_topics**: Number of topics tracked
- **total_mentions**: Total mentions across all topics
- **top_topics**: Top 10 topics by frequency (with counts)
- **trending_topics**: Topics with significant upward trends
- **new_topics**: Recently discovered topics

**Use Case**: Executive summary, dashboard KPIs, alerts.

---

### 4. `processor_state.json`
**Format**: JSON
**Description**: Complete system state including taxonomy and all daily counts.

**Contains**:
- **consolidated_topics**: List of canonical topics with metadata
  - canonical_name
  - variants (alternative phrasings)
  - description
  - category (issue/request/feedback)
- **topic_taxonomy**: Mapping from variant → canonical names
- **daily_topic_counts**: All daily counts for all topics
- **total_extractions**: Total number of review extractions

**Use Case**: Resume processing, regenerate reports, audit trail.

---

### 5. `sample_extractions.json`
**Format**: JSON
**Description**: Sample review extractions showing how AI processes individual reviews.

**Structure**:
```json
[
  {
    "review_id": "sample_1",
    "review_content": "Full review text...",
    "review_date": "ISO date",
    "review_score": 1-5,
    "topics": ["Topic 1", "Topic 2"],
    "sentiment": "negative|neutral|positive",
    "reasoning": "Explanation of topic assignment"
  }
]
```

**Use Case**: Understanding AI's topic extraction logic, quality assurance.

---

## Sample Data Notes

**Dataset**: 60 days of review data (June 1 - July 30, 2024)
**Topics**: 16 consolidated topics tracked
**Reviews**: Approximately 1,000+ reviews per day
**Coverage**: Food delivery app reviews

## Key Insights from Sample Data

### Top Issues (by total mentions):
1. **Feature request - faster delivery** (1,827 mentions)
   - Users requesting return of quick delivery options
   - Trend: -21.6% (declining mentions recently)

2. **Delivery partner rude** (1,527 mentions)
   - Complaints about delivery partner behavior
   - Trend: +3.7% (slight increase)

3. **Food arrived cold** (1,481 mentions)
   - Food temperature/quality issues
   - Trend: -20.4% (improving)

### Trending Up (Strong Growth):
- **Customer service unresponsive** (+73.3%)
- **Food portion reduced** (+63.5%)
- **Food quality poor/stale** (+33.0%)

These represent emerging or worsening issues requiring attention.

### Trending Down (Improving):
- **Maps/navigation issues** (-38.8%)
- **Delivery delay** (-26.6%)
- **Feature request - faster delivery** (-21.6%)

## How These Files Are Generated

### With Real Data:
```bash
python main.py --package com.application.zomato --start-date 2024-06-01
```

This will:
1. Scrape reviews from Google Play Store
2. Extract topics using AI agents (GPT-4)
3. Consolidate similar topics
4. Generate all report files

### With Sample Data (No API key needed):
```bash
python generate_sample_outputs.py
```

Generates realistic mock data to demonstrate system capabilities.

## Using These Files

### For Product Teams:
1. Open `trend_report_*.csv` in Excel
2. Review top topics and trends
3. Identify issues requiring immediate attention
4. Track improvements over time

### For Developers:
1. Use `trend_report_*.json` for API integration
2. Parse `processor_state.json` to resume processing
3. Analyze `sample_extractions.json` for quality checks

### For Executives:
1. Review `summary_*.json` for high-level metrics
2. Focus on "trending_topics" for emerging issues
3. Monitor "new_topics" for evolving concerns

## Report Interpretation Guide

### Understanding Trends:
- **Positive % (e.g., +25.3%)**: Topic mentions are increasing (worsening issue)
- **Negative % (e.g., -20.4%)**: Topic mentions are decreasing (improving)
- **"NEW"**: Topic appeared recently, no historical comparison

### Priority Matrix:
- **High Total + Positive Trend** = Critical priority (worsening major issue)
- **High Total + Negative Trend** = Monitor (major issue improving)
- **Low Total + Positive Trend** = Watch closely (emerging issue)
- **Low Total + Negative Trend** = Low priority (minor issue resolving)

## Next Steps

1. **Run with your app**: `python main.py --package your.app.package`
2. **Set up automation**: Schedule daily/weekly runs
3. **Integrate with tools**: Import JSON into your dashboards
4. **Take action**: Address top trending issues

---

**Version**: 1.0
**Last Updated**: December 2024
