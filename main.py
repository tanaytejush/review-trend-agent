"""Main application for Review Trend Analysis Agent.

This is the entry point for the agentic AI system that analyzes app store reviews
and generates trend reports.
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import json

from scrapers.play_store_scraper import PlayStoreScraper
from agents.batch_processor import BatchProcessor
from utils.report_generator import ReportGenerator
from config.config import (
    APP_PACKAGE_NAME,
    START_DATE,
    DATA_DIR,
    OUTPUT_DIR,
    TREND_WINDOW_DAYS
)


def scrape_reviews(package_name: str, start_date: datetime, end_date: datetime):
    """Scrape reviews and organize into daily batches.

    Args:
        package_name: App package name
        start_date: Start date for scraping
        end_date: End date for scraping
    """
    print("="*80)
    print("STEP 1: SCRAPING REVIEWS")
    print("="*80)

    scraper = PlayStoreScraper(package_name)

    # Get app info
    app_info = scraper.get_app_info()
    print(f"\nApp: {app_info.get('title')}")
    print(f"Score: {app_info.get('score')}")
    print(f"Total Reviews: {app_info.get('reviews_count')}\n")

    # Scrape reviews
    reviews = scraper.scrape_reviews(
        start_date=start_date,
        end_date=end_date,
        count=10000
    )

    print(f"\nScraped {len(reviews)} reviews")

    # Save all reviews
    scraper.save_reviews(reviews)

    # Organize into daily batches
    batches = scraper.organize_by_date(reviews)
    print(f"Organized into {len(batches)} daily batches")

    # Save daily batches
    scraper.save_daily_batches(batches)

    return batches


def process_batches(batch_dir: Path):
    """Process daily batches with AI agents.

    Args:
        batch_dir: Directory containing daily batch files
    """
    print("\n" + "="*80)
    print("STEP 2: PROCESSING BATCHES WITH AI AGENTS")
    print("="*80)

    # Find batch files
    batch_files = sorted(list(batch_dir.glob("reviews_*.json")))

    if not batch_files:
        print(f"No batch files found in {batch_dir}")
        return None

    print(f"\nFound {len(batch_files)} daily batch files")

    # Process batches
    processor = BatchProcessor()
    results = processor.process_multiple_batches(batch_files)

    print("\n--- Processing Summary ---")
    for result in results:
        print(f"{result['date']}: {result['reviews_count']} reviews, "
              f"{result['unique_topics']} unique topics")

    # Save processor state
    processor.save_state()

    return processor


def generate_reports(processor: BatchProcessor, target_date: str):
    """Generate trend analysis reports.

    Args:
        processor: BatchProcessor with processed data
        target_date: Target date for the report (T)
    """
    print("\n" + "="*80)
    print("STEP 3: GENERATING TREND REPORTS")
    print("="*80)

    # Get trend data
    trend_data = processor.get_trend_data(target_date, days=TREND_WINDOW_DAYS)

    print(f"\nGenerating report for date: {target_date}")
    print(f"Trend window: T-30 to T ({TREND_WINDOW_DAYS} days)")
    print(f"Total topics tracked: {len(trend_data)}")

    # Generate report
    generator = ReportGenerator()

    # Create DataFrame
    df = generator.generate_trend_table(trend_data, target_date)

    # Print text report
    generator.print_text_report(df, target_date, top_n=30)

    # Save reports in multiple formats
    csv_file = generator.save_csv_report(df, target_date)
    json_file = generator.save_json_report(trend_data, target_date)

    try:
        excel_file = generator.save_excel_report(df, target_date)
    except Exception as e:
        print(f"Could not save Excel report: {e}")
        print("Install openpyxl for Excel support: pip install openpyxl")

    # Generate summary stats
    stats = generator.generate_summary_stats(trend_data)

    print("\n--- Summary Statistics ---")
    print(f"Total Topics: {stats['total_topics']}")
    print(f"Total Mentions: {stats['total_mentions']}")

    print("\nTop 10 Topics:")
    for i, topic in enumerate(stats['top_topics'], 1):
        print(f"  {i}. {topic['topic']:40s} - {topic['total_mentions']} mentions")

    # Save summary
    summary_file = OUTPUT_DIR / f"summary_{target_date}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\nAll reports saved to: {OUTPUT_DIR}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="AI Agent for App Store Review Trend Analysis"
    )

    parser.add_argument(
        '--package',
        type=str,
        default=APP_PACKAGE_NAME,
        help='App package name (e.g., com.application.zomato)'
    )

    parser.add_argument(
        '--start-date',
        type=str,
        default=START_DATE.strftime("%Y-%m-%d"),
        help='Start date for reviews (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help='End date for reviews (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--target-date',
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help='Target date for report generation (T) (YYYY-MM-DD)'
    )

    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help='Only scrape reviews, do not process'
    )

    parser.add_argument(
        '--process-only',
        action='store_true',
        help='Only process existing batches, do not scrape'
    )

    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Only generate report from existing processor state'
    )

    args = parser.parse_args()

    # Parse dates
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    target_date = args.target_date

    print("\n" + "="*80)
    print("REVIEW TREND ANALYSIS AGENT")
    print("="*80)
    print(f"Package: {args.package}")
    print(f"Date Range: {args.start_date} to {args.end_date}")
    print(f"Target Date: {target_date}")
    print("="*80)

    batch_dir = DATA_DIR / "daily_batches"

    # Step 1: Scrape reviews
    if not args.process_only and not args.report_only:
        scrape_reviews(args.package, start_date, end_date)

    # Step 2: Process batches
    if not args.scrape_only and not args.report_only:
        processor = process_batches(batch_dir)
    elif args.report_only:
        # Load existing processor state
        processor = BatchProcessor()
        state_file = OUTPUT_DIR / "processor_state.json"
        if state_file.exists():
            processor.load_state(state_file)
        else:
            print(f"Processor state not found at {state_file}")
            print("Please run processing first.")
            return

    # Step 3: Generate reports
    if not args.scrape_only and processor:
        generate_reports(processor, target_date)

    print("\n" + "="*80)
    print("COMPLETED SUCCESSFULLY")
    print("="*80)


if __name__ == "__main__":
    main()
