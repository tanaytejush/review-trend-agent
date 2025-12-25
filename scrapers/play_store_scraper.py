"""Google Play Store review scraper with daily batch processing."""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from pathlib import Path

from google_play_scraper import app, reviews, Sort
from tqdm import tqdm
import pandas as pd

from config.config import APP_PACKAGE_NAME, DATA_DIR, CACHE_DIR, START_DATE


class PlayStoreScraper:
    """Scraper for Google Play Store reviews with batch processing."""

    def __init__(self, package_name: str = APP_PACKAGE_NAME):
        """Initialize the scraper.

        Args:
            package_name: Google Play package name (e.g., 'com.application.zomato')
        """
        self.package_name = package_name
        self.cache_file = CACHE_DIR / f"{package_name}_reviews.jsonl"

    def get_app_info(self) -> Dict:
        """Get basic app information."""
        try:
            app_info = app(self.package_name)
            return {
                "title": app_info.get("title"),
                "score": app_info.get("score"),
                "ratings": app_info.get("ratings"),
                "reviews_count": app_info.get("reviews")
            }
        except Exception as e:
            print(f"Error fetching app info: {e}")
            return {}

    def scrape_reviews(
        self,
        start_date: datetime = START_DATE,
        end_date: Optional[datetime] = None,
        count: int = 10000
    ) -> List[Dict]:
        """Scrape reviews from the Play Store.

        Args:
            start_date: Start date for reviews
            end_date: End date for reviews (default: today)
            count: Maximum number of reviews to fetch

        Returns:
            List of review dictionaries
        """
        if end_date is None:
            end_date = datetime.now()

        print(f"Scraping reviews for {self.package_name}")
        print(f"Date range: {start_date.date()} to {end_date.date()}")

        all_reviews = []
        continuation_token = None

        try:
            # Fetch reviews in batches
            while len(all_reviews) < count:
                result, continuation_token = reviews(
                    self.package_name,
                    lang='en',
                    country='us',
                    sort=Sort.NEWEST,
                    count=200,
                    continuation_token=continuation_token
                )

                if not result:
                    break

                # Filter by date range
                for review in result:
                    review_date = review['at']

                    if review_date < start_date:
                        # Reached reviews older than start date, stop
                        return all_reviews

                    if start_date <= review_date <= end_date:
                        all_reviews.append({
                            'review_id': review.get('reviewId'),
                            'user_name': review.get('userName'),
                            'content': review.get('content'),
                            'score': review.get('score'),
                            'thumbs_up': review.get('thumbsUpCount'),
                            'date': review_date.isoformat(),
                            'reply_content': review.get('replyContent'),
                            'reply_date': review.get('repliedAt').isoformat() if review.get('repliedAt') else None
                        })

                print(f"Fetched {len(all_reviews)} reviews so far...")

                if continuation_token is None:
                    break

                # Rate limiting
                time.sleep(1)

        except Exception as e:
            print(f"Error during scraping: {e}")

        return all_reviews

    def organize_by_date(self, reviews: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize reviews by date (daily batches).

        Args:
            reviews: List of review dictionaries

        Returns:
            Dictionary with date as key and list of reviews as value
        """
        batches = {}

        for review in reviews:
            review_date = datetime.fromisoformat(review['date']).date()
            date_key = review_date.isoformat()

            if date_key not in batches:
                batches[date_key] = []

            batches[date_key].append(review)

        return batches

    def save_reviews(self, reviews: List[Dict], filename: Optional[str] = None):
        """Save reviews to JSON file.

        Args:
            reviews: List of review dictionaries
            filename: Output filename (default: auto-generated)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reviews_{self.package_name}_{timestamp}.json"

        filepath = DATA_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(reviews)} reviews to {filepath}")
        return filepath

    def save_daily_batches(self, batches: Dict[str, List[Dict]]):
        """Save daily batches to separate files.

        Args:
            batches: Dictionary of date -> reviews
        """
        batch_dir = DATA_DIR / "daily_batches"
        batch_dir.mkdir(exist_ok=True)

        for date_key, day_reviews in batches.items():
            filename = f"reviews_{date_key}.json"
            filepath = batch_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(day_reviews, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(batches)} daily batch files to {batch_dir}")

    def load_reviews(self, filepath: Path) -> List[Dict]:
        """Load reviews from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


def main():
    """Main function to test the scraper."""
    scraper = PlayStoreScraper()

    # Get app info
    app_info = scraper.get_app_info()
    print(f"App: {app_info.get('title')}")
    print(f"Score: {app_info.get('score')}")
    print(f"Total Reviews: {app_info.get('reviews_count')}")
    print()

    # Scrape reviews
    reviews = scraper.scrape_reviews(
        start_date=START_DATE,
        count=5000
    )

    print(f"\nTotal reviews scraped: {len(reviews)}")

    # Organize by date
    batches = scraper.organize_by_date(reviews)
    print(f"Days with reviews: {len(batches)}")

    # Save
    scraper.save_reviews(reviews)
    scraper.save_daily_batches(batches)


if __name__ == "__main__":
    main()
