"""Generate trend analysis reports in various formats."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from config.config import OUTPUT_DIR, TREND_WINDOW_DAYS


class ReportGenerator:
    """Generate trend analysis reports from processed review data."""

    def __init__(self):
        """Initialize the report generator."""
        pass

    def generate_trend_table(
        self,
        trend_data: Dict[str, Dict[str, int]],
        target_date: str,
        days: int = TREND_WINDOW_DAYS
    ) -> pd.DataFrame:
        """Generate trend table as DataFrame.

        Args:
            trend_data: Dictionary of {topic: {date: count}}
            target_date: Target date (T)
            days: Number of days to include (31 for T to T-30)

        Returns:
            DataFrame with topics as rows, dates as columns
        """
        # Calculate date range
        end_date = datetime.strptime(target_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=days - 1)

        # Generate date columns
        date_range = []
        current = start_date
        while current <= end_date:
            date_range.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

        # Build table data
        table_data = []

        for topic, date_counts in trend_data.items():
            row = {'Topic': topic}

            for date in date_range:
                # Use shorter date format for columns (Mon DD or Jun 01)
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                col_name = date_obj.strftime("%b %d")
                row[col_name] = date_counts.get(date, 0)

            # Calculate total and trend
            counts = [date_counts.get(date, 0) for date in date_range]
            row['Total'] = sum(counts)

            # Calculate trend (simple: compare last 7 days vs previous 7 days)
            if len(counts) >= 14:
                recent_avg = sum(counts[-7:]) / 7
                previous_avg = sum(counts[-14:-7]) / 7
                if previous_avg > 0:
                    trend_pct = ((recent_avg - previous_avg) / previous_avg) * 100
                    row['Trend'] = f"{trend_pct:+.1f}%"
                else:
                    row['Trend'] = "NEW" if recent_avg > 0 else "-"
            else:
                row['Trend'] = "-"

            table_data.append(row)

        # Create DataFrame
        df = pd.DataFrame(table_data)

        # Sort by Total descending
        df = df.sort_values('Total', ascending=False)

        return df

    def save_csv_report(
        self,
        df: pd.DataFrame,
        target_date: str,
        filename: Optional[str] = None
    ):
        """Save report as CSV.

        Args:
            df: DataFrame to save
            target_date: Target date for filename
            filename: Custom filename (optional)
        """
        if filename is None:
            filename = f"trend_report_{target_date}.csv"

        filepath = OUTPUT_DIR / filename
        df.to_csv(filepath, index=False)

        print(f"Saved CSV report to {filepath}")
        return filepath

    def save_excel_report(
        self,
        df: pd.DataFrame,
        target_date: str,
        filename: Optional[str] = None
    ):
        """Save report as Excel with formatting.

        Args:
            df: DataFrame to save
            target_date: Target date for filename
            filename: Custom filename (optional)
        """
        if filename is None:
            filename = f"trend_report_{target_date}.xlsx"

        filepath = OUTPUT_DIR / filename

        # Create Excel writer with styling
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Trend Analysis')

            # Get worksheet
            worksheet = writer.sheets['Trend Analysis']

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        print(f"Saved Excel report to {filepath}")
        return filepath

    def save_json_report(
        self,
        trend_data: Dict[str, Dict[str, int]],
        target_date: str,
        metadata: Optional[Dict] = None,
        filename: Optional[str] = None
    ):
        """Save report as JSON.

        Args:
            trend_data: Dictionary of {topic: {date: count}}
            target_date: Target date
            metadata: Additional metadata to include
            filename: Custom filename (optional)
        """
        if filename is None:
            filename = f"trend_report_{target_date}.json"

        filepath = OUTPUT_DIR / filename

        report = {
            'target_date': target_date,
            'generated_at': datetime.now().isoformat(),
            'trend_data': trend_data,
            'metadata': metadata or {}
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Saved JSON report to {filepath}")
        return filepath

    def generate_summary_stats(
        self,
        trend_data: Dict[str, Dict[str, int]]
    ) -> Dict:
        """Generate summary statistics.

        Args:
            trend_data: Dictionary of {topic: {date: count}}

        Returns:
            Dictionary with summary stats
        """
        stats = {
            'total_topics': len(trend_data),
            'total_mentions': 0,
            'top_topics': [],
            'trending_topics': [],
            'new_topics': []
        }

        # Calculate totals and find top topics
        topic_totals = []

        for topic, date_counts in trend_data.items():
            total = sum(date_counts.values())
            stats['total_mentions'] += total

            topic_totals.append({
                'topic': topic,
                'total_mentions': total
            })

        # Sort and get top 10
        topic_totals.sort(key=lambda x: x['total_mentions'], reverse=True)
        stats['top_topics'] = topic_totals[:10]

        return stats

    def print_text_report(
        self,
        df: pd.DataFrame,
        target_date: str,
        top_n: int = 20
    ):
        """Print formatted text report to console.

        Args:
            df: DataFrame with trend data
            target_date: Target date
            top_n: Number of top topics to display
        """
        print(f"\n{'='*80}")
        print(f"TREND ANALYSIS REPORT")
        print(f"Target Date: {target_date}")
        print(f"Window: T-30 to T ({TREND_WINDOW_DAYS} days)")
        print(f"{'='*80}\n")

        # Show top N topics
        print(f"TOP {top_n} TOPICS BY TOTAL MENTIONS:\n")

        display_df = df.head(top_n)

        # Show simplified view
        cols_to_show = ['Topic', 'Total', 'Trend']

        for idx, row in display_df.iterrows():
            print(f"{row['Topic']:50s} | Total: {row['Total']:4d} | Trend: {row['Trend']:>8s}")

        print(f"\n{'='*80}")


def main():
    """Test the report generator."""
    # Sample trend data
    sample_trend_data = {
        "Delivery delay": {
            "2024-06-01": 12, "2024-06-02": 8, "2024-06-03": 15,
            "2024-06-04": 10, "2024-06-05": 20
        },
        "Food arrived cold": {
            "2024-06-01": 5, "2024-06-02": 7, "2024-06-03": 3,
            "2024-06-04": 8, "2024-06-05": 11
        },
        "Delivery partner rude": {
            "2024-06-01": 8, "2024-06-02": 12, "2024-06-03": 6,
            "2024-06-04": 9, "2024-06-05": 7
        }
    }

    generator = ReportGenerator()

    # Generate reports
    df = generator.generate_trend_table(sample_trend_data, "2024-06-05", days=5)

    print("DataFrame:")
    print(df)

    # Save reports
    generator.save_csv_report(df, "2024-06-05", "sample_report.csv")
    generator.save_json_report(sample_trend_data, "2024-06-05", filename="sample_report.json")

    # Print text report
    generator.print_text_report(df, "2024-06-05")

    # Summary stats
    stats = generator.generate_summary_stats(sample_trend_data)
    print("\nSummary Statistics:")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
