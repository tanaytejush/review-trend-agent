# Review Trend Agent

Review Trend Agent turns a large volume of Google Play Store reviews into
actionable product and operations trends.

## The problem it solves

Teams receive thousands of reviews, but manually reading them does not scale.
Keyword-based topic modelling also fragments one problem into many labels:
"delivery is late", "slow delivery", and "order arrived late" may appear as
separate topics.

This project uses an LLM to understand review context, extracts meaningful
topics, consolidates similar wording into canonical topics, counts those
topics by day, and exports trend reports for analysts.

**Core message:** it transforms noisy customer feedback into a consistent,
time-based view of what customers need fixed, improved, or preserved.

For a plain-language walkthrough, see [SIMPLE_EXPLANATION.md](SIMPLE_EXPLANATION.md).

## What it does

1. Fetches reviews for a Google Play application.
2. Filters reviews by date and stores daily JSON batches.
3. Extracts topics, sentiment, and reasoning in LLM batches.
4. Consolidates duplicate or semantically equivalent topics.
5. Builds a topic-by-day trend matrix.
6. Writes CSV, JSON, Excel, and summary JSON reports.

## Project structure

| Path | Purpose |
|---|---|
| `main.py` | CLI pipeline: scrape, process, and report |
| `scrapers/` | Google Play review collection |
| `agents/topic_extraction_agent.py` | Contextual topic extraction |
| `agents/topic_consolidation_agent.py` | Canonical topic taxonomy |
| `agents/batch_processor.py` | Daily processing and state management |
| `utils/report_generator.py` | CSV, JSON, Excel, and summary reports |
| `config/config.py` | Environment-based configuration |
| `output/` | Sample reports and generated state |

## Setup

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
Copy-Item .env.example .env  # Windows PowerShell
# cp .env.example .env       # macOS/Linux
```

Set `OPENAI_API_KEY` in `.env`. The default application package is
`com.application.zomato`; override it with `APP_PACKAGE_NAME`.

## Run the pipeline

```bash
python main.py `
  --package com.application.zomato `
  --start-date 2024-06-01 `
  --end-date 2024-06-30 `
  --target-date 2024-06-30
```

On macOS/Linux, replace PowerShell backticks with backslashes or use one line:

```bash
python main.py --package com.application.zomato --start-date 2024-06-01 --end-date 2024-06-30 --target-date 2024-06-30
```

Useful modes:

```bash
python main.py --scrape-only
python main.py --process-only --target-date 2024-06-30
python main.py --report-only --target-date 2024-06-30
```

Generated files are written to `output/`:

- `trend_report_<date>.csv`
- `trend_report_<date>.json`
- `trend_report_<date>.xlsx` (when `openpyxl` is installed)
- `summary_<date>.json`
- `processor_state.json`

## Configuration

Configuration is read from `.env` and `config/config.py`; there is no
`run_agent.py` or `config.yaml` entry point.

Important settings include:

```dotenv
APP_PACKAGE_NAME=com.application.zomato
START_DATE=2024-06-01
TOPIC_EXTRACTION_MODEL=gpt-4-turbo-preview
TOPIC_CONSOLIDATION_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.3
MAX_RETRIES=3
```

## Design notes

- Reviews are processed in batches to control model cost.
- The processor saves topic counts and taxonomy state so reports can be
  regenerated without re-running extraction.
- The extraction response uses a validated `extractions` JSON object.
- Reports compare the latest seven days with the preceding seven days and
  identify growing and newly appearing topics.

## Development

Compile the project without making API calls:

```bash
python -m compileall -q .
```

Run deterministic tests:

```bash
python -m unittest discover -s tests -v
```

## Limitations

- The current scraper supports Google Play only.
- Reviews are currently requested in English from the US Play Store locale.
- LLM calls require an OpenAI API key.
- Large-scale production use should add persistent review-ID deduplication,
  extraction caching, structured logging, and a database backend.

## License

See [LICENSE](LICENSE).
