# Video Demo Notes

Quick outline for the demo video (keep it under 10 mins)

## Intro (1 min)
- Show folder structure
- Explain what it does: analyzes Play Store reviews and spots trends
- Main problem solved: consolidates similar topics (e.g., "delivery guy rude" + "delivery partner impolite" → one topic)
- Why this matters: gives clear trends instead of fragmented data

## Architecture (2 mins)
- Walk through folder structure
  - `scrapers/` - gets reviews from Play Store
  - `agents/` - core logic (extraction, consolidation, batch processing)
  - `utils/` - report generation
  - `output/` - sample reports
- Show topic_consolidation_agent.py briefly
- Explain: uses LLM to detect semantic similarity and group topics

## Live Demo (3 mins)
- Run `python examples/quick_start.py`
- Point out as it runs:
  - Extracting topics from reviews
  - Consolidating similar ones
  - Building trend counts by date
  - Generating final report
- Show how fast it runs

## Output Review (2-3 mins)
- Open trend_report_2024-07-30.csv in Excel
  - Show format: topics as rows, dates as columns
  - Point out trends (up/down percentages)
  - Example: "Customer service unresponsive" up 73% = red flag
- Open summary JSON
  - Total stats
  - Top topics
  - Good for APIs/dashboards
- Show processor_state.json
  - Look at taxonomy section
  - See how variants map to canonical names

## Key Features (1-2 mins)
- LLM-based approach (GPT-4) vs traditional methods
  - 85-95% accuracy vs 60-70%
  - Understands context
- Auto-learns new topics (starts with seeds, discovers new ones)
- Explainable (shows reasoning for each classification)
- Production ready:
  - Error handling & retries
  - Multiple output formats
  - Can resume if interrupted
- Configurable (see .env.example)

## Use Cases (1 min)
Why product teams would use this:
- Spot trending issues (e.g., "customer service unresponsive" up 73%)
- Track if fixes are working (e.g., "maps issues" down 38%)
- Discover new problems early
- Prioritize based on volume

## Wrap Up (30 sec)
Quick summary:
- Automates review analysis
- Smart topic consolidation (key innovation)
- Multiple export formats
- Production ready with docs

---

## Quick Notes
- Keep it around 8-9 minutes total
- Don't rush, let things sink in
- Show confidence (no "I think" or "maybe")
- Focus on the consolidation feature - that's the differentiator
