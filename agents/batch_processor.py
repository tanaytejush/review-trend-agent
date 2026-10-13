"""Daily batch processing pipeline for review analysis."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

from agents.topic_extraction_agent import TopicExtractionAgent
from agents.topic_consolidation_agent import TopicConsolidationAgent
from config.config import DATA_DIR, OUTPUT_DIR


class BatchProcessor:
    """Process daily review batches and build topic trends over time."""

    def __init__(self):
        """Initialize the batch processor with agents."""
        self.extraction_agent = TopicExtractionAgent()
        self.consolidation_agent = TopicConsolidationAgent()

        self.consolidated_topics = []  # List of canonical topic groups
        self.daily_topic_counts = defaultdict(lambda: defaultdict(int))  # {date: {topic: count}}
        self.all_extractions = []  # All extractions for reference

    def process_daily_batch(
        self,
        date: str,
        reviews: List[Dict],
        update_taxonomy: bool = True
    ) -> Dict:
        """Process a single day's batch of reviews.

        Args:
            date: Date string (YYYY-MM-DD)
            reviews: List of review dictionaries
            update_taxonomy: Whether to update the topic taxonomy with new findings

        Returns:
            Processing results for the day
        """
        print(f"\nProcessing batch for {date} ({len(reviews)} reviews)...")

        # Step 1: Extract topics from reviews
        extractions = self.extraction_agent.extract_topics(
            reviews,
            batch_size=10,
            existing_topics=[t['canonical_name'] for t in self.consolidated_topics]
        )

        # Step 2: Get all unique topics from this batch
        unique_topics = self.extraction_agent.get_all_unique_topics(extractions)

        print(f"  Extracted {len(unique_topics)} unique topics")

        # Step 3: Consolidate topics (incremental consolidation with existing taxonomy)
        if update_taxonomy and unique_topics:
            consolidated, new_topics = self.consolidation_agent.incremental_consolidation(
                unique_topics,
                self.consolidated_topics
            )
            self.consolidated_topics = consolidated

            if new_topics:
                print(f"  Found {len(new_topics)} new topics: {new_topics}")

        # Step 4: Map extracted topics to canonical forms and count
        for extraction in extractions:
            for topic in extraction.get('topics', []):
                canonical_topic = self.consolidation_agent.map_to_canonical(topic)
                self.daily_topic_counts[date][canonical_topic] += 1

        # Store extractions
        self.all_extractions.extend(extractions)

        return {
            'date': date,
            'reviews_count': len(reviews),
            'extractions_count': len(extractions),
            'unique_topics': len(unique_topics),
            'topic_counts': dict(self.daily_topic_counts[date])
        }

    def process_multiple_batches(
        self,
        batch_files: List[Path]
    ) -> List[Dict]:
        """Process multiple daily batch files.

        Args:
            batch_files: List of paths to daily batch JSON files

        Returns:
            List of processing results for each day
        """
        results = []

        # Sort files by date
        sorted_files = sorted(batch_files, key=lambda x: x.stem.split('_')[-1])

        for batch_file in sorted_files:
            # Extract date from filename (format: reviews_YYYY-MM-DD.json)
            date = batch_file.stem.split('_')[-1]

            # Load reviews
            with open(batch_file, 'r', encoding='utf-8') as f:
                reviews = json.load(f)

            # Process batch
            result = self.process_daily_batch(date, reviews)
            results.append(result)

        return results

    def get_trend_data(
        self,
        end_date: str,
        days: int = 31
    ) -> Dict[str, Dict[str, int]]:
        """Get trend data for the last N days ending on end_date.

        Args:
            end_date: End date (YYYY-MM-DD)
            days: Number of days to include (default 31 for T to T-30)

        Returns:
            Dictionary of {topic: {date: count}}
        """
        end = datetime.strptime(end_date, "%Y-%m-%d")
        start = end - timedelta(days=days - 1)

        # Generate all dates in range
        date_range = []
        current = start
        while current <= end:
            date_range.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # Build trend data structure
        trend_data = defaultdict(dict)

        # Get all canonical topics
        all_topics = set()
        for date in date_range:
            all_topics.update(self.daily_topic_counts.get(date, {}).keys())

        # Fill in data (0 for missing days)
        for topic in all_topics:
            for date in date_range:
                count = self.daily_topic_counts.get(date, {}).get(topic, 0)
                trend_data[topic][date] = count

        return dict(trend_data)

    def save_state(self, filepath: Optional[Path] = None):
        """Save processor state (taxonomy, counts, etc.)

        Args:
            filepath: Path to save state (default: output/processor_state.json)
        """
        if filepath is None:
            filepath = OUTPUT_DIR / "processor_state.json"

        state = {
            'consolidated_topics': self.consolidated_topics,
            'topic_taxonomy': self.consolidation_agent.get_taxonomy(),
            'daily_topic_counts': {
                date: dict(counts) for date, counts in self.daily_topic_counts.items()
            },
            'total_extractions': len(self.all_extractions)
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print(f"Saved processor state to {filepath}")

    def load_state(self, filepath: Path):
        """Load processor state from file.

        Args:
            filepath: Path to state file
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)

        self.consolidated_topics = state.get('consolidated_topics', [])
        self.consolidation_agent.topic_taxonomy = state.get('topic_taxonomy', {})

        # Restore daily counts
        for date, counts in state.get('daily_topic_counts', {}).items():
            self.daily_topic_counts[date] = defaultdict(int, counts)

        print(f"Loaded processor state from {filepath}")


def main():
    """Test the batch processor."""
    # Look for daily batch files
    batch_dir = DATA_DIR / "daily_batches"

    if not batch_dir.exists():
        print(f"Batch directory not found: {batch_dir}")
        print("Please run the scraper first to generate daily batches.")
        return

    batch_files = list(batch_dir.glob("reviews_*.json"))

    if not batch_files:
        print(f"No batch files found in {batch_dir}")
        return

    print(f"Found {len(batch_files)} batch files")

    # Process batches
    processor = BatchProcessor()
    results = processor.process_multiple_batches(batch_files)

    print("\n=== Processing Summary ===")
    for result in results:
        print(f"{result['date']}: {result['reviews_count']} reviews, "
              f"{result['unique_topics']} unique topics")

    # Save state
    processor.save_state()

    print("\n=== Consolidated Topics ===")
    for i, topic_group in enumerate(processor.consolidated_topics[:10], 1):
        print(f"{i}. {topic_group['canonical_name']}")
        print(f"   Variants: {', '.join(topic_group.get('variants', []))}")
        print(f"   Category: {topic_group.get('category', 'N/A')}")


if __name__ == "__main__":
    main()
