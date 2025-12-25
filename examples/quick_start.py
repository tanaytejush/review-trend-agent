"""Quick start example for the Review Trend Analysis Agent.

This script demonstrates the basic usage of the system.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.play_store_scraper import PlayStoreScraper
from agents.topic_extraction_agent import TopicExtractionAgent
from agents.topic_consolidation_agent import TopicConsolidationAgent
from utils.report_generator import ReportGenerator


def demo_with_sample_reviews():
    """Demonstrate the system with sample reviews."""

    print("="*80)
    print("REVIEW TREND ANALYSIS AGENT - QUICK START DEMO")
    print("="*80)

    # Sample reviews (simulating data from June 2024)
    sample_reviews = [
        # Day 1
        {
            "review_id": "1",
            "content": "Delivery guy was extremely rude to me. Threw the food at my door.",
            "date": "2024-06-01",
            "score": 1
        },
        {
            "review_id": "2",
            "content": "Food arrived completely cold and the packaging was damaged.",
            "date": "2024-06-01",
            "score": 1
        },
        {
            "review_id": "3",
            "content": "App keeps crashing when I try to apply discount codes!",
            "date": "2024-06-01",
            "score": 2
        },
        # Day 2
        {
            "review_id": "4",
            "content": "Delivery partner was very impolite and didn't follow instructions",
            "date": "2024-06-02",
            "score": 1
        },
        {
            "review_id": "5",
            "content": "The food quality was terrible. Everything was stale.",
            "date": "2024-06-02",
            "score": 1
        },
        {
            "review_id": "6",
            "content": "Please bring back the 10 minute delivery option! It was so convenient.",
            "date": "2024-06-02",
            "score": 3
        },
        # Day 3
        {
            "review_id": "7",
            "content": "Delivery person behaved badly and was unprofessional",
            "date": "2024-06-03",
            "score": 1
        },
        {
            "review_id": "8",
            "content": "Food came cold again. This is the third time this week!",
            "date": "2024-06-03",
            "score": 1
        },
        {
            "review_id": "9",
            "content": "Application freezes constantly. Can't even place an order.",
            "date": "2024-06-03",
            "score": 1
        },
        {
            "review_id": "10",
            "content": "Fast delivery but the app needs major improvements",
            "date": "2024-06-03",
            "score": 3
        }
    ]

    print(f"\n📝 Processing {len(sample_reviews)} sample reviews...")

    # Step 1: Extract topics using AI agent
    print("\n" + "-"*80)
    print("STEP 1: Topic Extraction with AI Agent")
    print("-"*80)

    extraction_agent = TopicExtractionAgent()
    extractions = extraction_agent.extract_topics(sample_reviews, batch_size=5)

    print(f"\n✓ Extracted topics from {len(extractions)} reviews")

    # Show some extractions
    print("\nSample Extractions:")
    for i, ext in enumerate(extractions[:3], 1):
        print(f"\n  Review {i}: \"{ext.get('review_content', '')[:60]}...\"")
        print(f"  Topics: {ext.get('topics', [])}")
        print(f"  Sentiment: {ext.get('sentiment', 'N/A')}")

    # Get all unique topics
    unique_topics = extraction_agent.get_all_unique_topics(extractions)
    print(f"\n✓ Found {len(unique_topics)} unique topics:")
    for topic in unique_topics:
        print(f"  - {topic}")

    # Step 2: Consolidate topics using AI agent
    print("\n" + "-"*80)
    print("STEP 2: Topic Consolidation (Solving Duplication Problem)")
    print("-"*80)

    consolidation_agent = TopicConsolidationAgent()
    consolidation = consolidation_agent.consolidate_topics(unique_topics)

    print("\n✓ Consolidated into canonical topics:")
    for topic_group in consolidation.get('consolidated_topics', []):
        canonical = topic_group['canonical_name']
        variants = topic_group.get('variants', [])
        print(f"\n  📌 {canonical}")
        if len(variants) > 1:
            print(f"     Consolidated from: {', '.join(variants)}")
        print(f"     Category: {topic_group.get('category', 'N/A')}")

    # Step 3: Build trend data
    print("\n" + "-"*80)
    print("STEP 3: Building Trend Data")
    print("-"*80)

    # Count topics by date
    from collections import defaultdict
    daily_counts = defaultdict(lambda: defaultdict(int))

    for extraction in extractions:
        date = extraction.get('review_date', '')[:10]  # YYYY-MM-DD
        for topic in extraction.get('topics', []):
            canonical_topic = consolidation_agent.map_to_canonical(topic)
            daily_counts[date][canonical_topic] += 1

    # Build trend data structure
    trend_data = {}
    for topic_group in consolidation.get('consolidated_topics', []):
        canonical = topic_group['canonical_name']
        trend_data[canonical] = {}

        for date in ['2024-06-01', '2024-06-02', '2024-06-03']:
            trend_data[canonical][date] = daily_counts[date].get(canonical, 0)

    print("\n✓ Trend data built successfully")

    # Step 4: Generate report
    print("\n" + "-"*80)
    print("STEP 4: Generating Trend Report")
    print("-"*80)

    generator = ReportGenerator()
    df = generator.generate_trend_table(trend_data, "2024-06-03", days=3)

    print("\n📊 TREND REPORT (Sample - 3 days)")
    print("="*80)
    print(df.to_string(index=False))

    print("\n" + "="*80)
    print("✓ DEMO COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nKey Achievements Demonstrated:")
    print("  ✓ Agentic AI topic extraction (not traditional LDA/TopicBERT)")
    print("  ✓ Smart topic consolidation to prevent duplicates")
    print("  ✓ Daily batch processing")
    print("  ✓ Trend analysis over time")
    print("\nTo run with real data:")
    print("  python main.py --package com.application.zomato")
    print()


if __name__ == "__main__":
    demo_with_sample_reviews()
