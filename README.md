# Review Trend Agent

## Problem Statement

Customer reviews contain the most unfiltered signal about what is working and what is broken in a product — but at any meaningful scale, no analyst can read thousands of reviews daily. Traditional topic modelling tools (LDA, NMF) surface clusters of keywords, not insights. They require an ML practitioner to interpret the output, and they collapse by the time customers start using new language to describe the same problem. This pipeline extracts actionable trend signals from high-volume review streams and delivers them in formats that fit how operations teams already work.

## Who It's For

**Operations teams and product analysts** who need a daily summary of what customers are saying — without running code, reading a Jupyter notebook, or interpreting a topic model. The pipeline runs on a schedule and exports results to CSV, JSON, and Excel, so the output lands directly in the tools analysts already use.

## Key Product Decisions

**Why replace LDA topic modelling with LLM-based contextual understanding?**
LDA groups documents by co-occurring words. It cannot tell the difference between "the app crashed" and "I'm crashing on this app, it's so addictive" — both contain "crash" and "app." LLMs understand intent and context. The tradeoff is compute cost: LLM inference is more expensive per review than LDA. The decision was made deliberately — signal quality was more valuable than cost savings, because a low-quality topic cluster that an analyst cannot act on has zero value regardless of how cheaply it was produced.

**Why build semantic deduplication?**
Without deduplication, a trend report would show "login issues," "can't log in," "login broken," and "sign-in not working" as four separate trends, each with a fraction of the true signal weight. Semantic deduplication embeds all trend phrases and consolidates variants that are semantically equivalent into a single canonical topic with an accurate frequency count. This makes the output immediately readable without manual post-processing by the analyst.

**Why export to CSV, JSON, and Excel instead of building a dashboard?**
The target user is an ops analyst or team lead who already has workflows built around spreadsheets and data pipelines. Building a proprietary dashboard would have required them to adopt a new tool and change their workflow. Meeting users where they already are — in Excel and their existing BI tools — was a faster path to adoption than building something they would have to learn.

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangChain multi-agent pipeline |
| Language model | LLM-based contextual topic extraction |
| Semantic deduplication | Sentence embeddings + clustering |
| Data processing | Python, pandas |
| Output formats | CSV, JSON, Excel (.xlsx) |

## How To Run

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY=your_key_here

# Run the pipeline against a reviews file
python run_agent.py --input reviews.csv --output results/

# Output files will appear in results/ as trends.csv, trends.json, trends.xlsx
```

The pipeline processes reviews in batches to manage API costs. Batch size and the confidence threshold for semantic deduplication are configurable in `config.yaml`.
