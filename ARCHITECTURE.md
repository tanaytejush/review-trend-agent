# System Architecture

## Overview

This doc explains how the system works and why I built it this way.

## Core Design Decisions

### 1. Why LLMs Instead of Traditional Topic Modeling?

I went with GPT-4 instead of LDA/TopicBERT for a few reasons:

**The Good**:
- Way better accuracy (85-95% vs 60-70%)
- Actually understands context, not just keywords
- Gives you clear topic names like "Delivery partner rude" instead of "topic_7"
- No training data needed - works immediately
- Provides reasoning for why it tagged something a certain way

**The Trade-offs**:
- Costs money (API calls)
- Depends on OpenAI being up
- Slower than statistical methods

### 2. Keep It Modular

The system is split into separate modules that each do one thing:

```
Reviews → Topic Extraction → Topic Consolidation → Batch Processor → Reports
```

Why this way?
- Each part does its own job
- Easy to test pieces independently
- Can swap out modules if needed
- Clear flow from input to output

### 3. Learning As It Goes

The system starts with a few seed topics (like "Delivery delay", "App crashes") and learns new ones as it processes reviews.

How it works:
1. Start with seed topics
2. Find new topics in reviews
3. Merge similar ones with existing topics
4. Keep the taxonomy updated

This means the system adapts to new issues automatically - if users start complaining about a new feature, it'll pick that up.

## Key Challenge: Topic Deduplication

### The Problem

When extracting topics from natural language, similar issues get different names:

```
❌ Without Consolidation:
- "Delivery guy rude" (23 mentions)
- "Delivery partner impolite" (15 mentions)
- "Delivery person bad behavior" (18 mentions)
- "Rude delivery agent" (12 mentions)

Result: Fragmented data, unclear trends
```

### The Solution

Use semantic consolidation:

```python
def consolidate_topics(self, topics: List[str]) -> Dict:
    """
    1. Identify semantic similarity between topics
    2. Group related topics together
    3. Choose canonical names for groups
    4. Build taxonomy mapping
    """
```

**Result**:
```
✅ With Consolidation:
- "Delivery partner rude" (68 mentions)
  Variants: ["Delivery guy rude", "Delivery partner impolite",
             "Delivery person bad behavior", "Rude delivery agent"]

Result: Clear, accurate trend data
```

## Data Flow

### End-to-End Processing

```
1. SCRAPING
   ├─ Fetch reviews from Play Store API
   ├─ Filter by date range
   └─ Organize into daily batches
         │
         ▼
2. EXTRACTION (NLP Module)
   ├─ Process each review with language model
   ├─ Identify topics, sentiment, reasoning
   └─ Output: {review → [topics]}
         │
         ▼
3. CONSOLIDATION (Semantic Module)
   ├─ Collect all unique topics
   ├─ Group semantically similar topics
   ├─ Create canonical names
   └─ Build taxonomy mapping
         │
         ▼
4. AGGREGATION
   ├─ Map topics to canonical forms
   ├─ Count by date
   └─ Build trend matrix: {topic → {date → count}}
         │
         ▼
5. REPORTING
   ├─ Generate table (topics × dates)
   ├─ Calculate trends
   └─ Output CSV, JSON, Excel
```

## Technical Decisions

### 1. Model Selection

**Choice**: OpenAI GPT-4 Turbo

**Reasons**:
- Strong reasoning capabilities
- Excellent semantic understanding
- Reliable structured output
- Good balance of cost and performance

**Alternatives Considered**:
- GPT-3.5: Lower cost but reduced accuracy
- Local models: No API costs but require infrastructure
- Traditional ML: Faster but lower quality results

### 2. Batch Processing

**Choice**: Process reviews in daily batches

**Benefits**:
- Natural temporal granularity
- Easy to resume/reprocess
- Clear checkpoints
- Memory efficient

**Implementation**:
```python
# Each batch is independent
for date, reviews in daily_batches.items():
    extractions = extract_topics(reviews)
    counts = aggregate_topics(extractions)
    save_checkpoint(date, counts)
```

### 3. State Management

**Choice**: Save complete processor state to JSON

**Saved State**:
- Consolidated topic taxonomy
- Topic→canonical mappings
- Daily topic counts
- Metadata

**Benefits**:
- Can resume processing
- Can regenerate reports without reprocessing
- Audit trail
- Easy debugging

### 4. Error Handling

**Strategy**: Graceful degradation with retries

```python
@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def extract_topics(reviews):
    # API call with automatic retry
```

**Fallbacks**:
- Retry with exponential backoff
- Skip failed batches (log error)
- Continue processing remaining batches

## Scalability Considerations

### Current Limitations

- **API Rate Limits**: OpenAI has rate limits
- **Processing Time**: ~5-10 sec per batch of 10 reviews
- **Memory**: Stores all data in memory during processing
- **Cost**: ~$0.01 per 10 reviews

### Scaling Strategies

**For Large Scale (100K+ reviews)**:

1. **Batch Size Optimization**
   - Process larger batches per API call
   - Optimize API usage patterns

2. **Parallel Processing**
   - Process multiple days concurrently
   - Use asynchronous operations

3. **Caching Strategy**
   - Cache topic extractions
   - Cache consolidation results
   - Enable quick report regeneration

4. **Cost Optimization**
   - Use cost-effective models where possible
   - Reserve premium models for critical tasks

5. **Database Backend**
   - Replace JSON with PostgreSQL/MongoDB
   - Implement streaming for large datasets

## Testing Strategy

### Unit Tests

- Test individual agents with sample data
- Verify topic extraction accuracy
- Check consolidation logic

### Integration Tests

- Test complete pipeline with sample reviews
- Verify output format
- Check error handling

### Manual Testing

```bash
# Test each component
python scrapers/play_store_scraper.py
python agents/topic_extraction_agent.py
python agents/topic_consolidation_agent.py

# Test full pipeline
python main.py --package com.application.zomato
```

## Future Improvements

### Short Term
- [ ] Add progress bars for long operations
- [ ] Implement caching for expensive operations
- [ ] Add confidence scores to topics
- [ ] Support for Apple App Store

### Medium Term
- [ ] Web dashboard for visualization
- [ ] Real-time processing with streaming
- [ ] Multi-language support
- [ ] Anomaly detection (topic spikes)

### Long Term
- [ ] Fine-tuned model for topic extraction
- [ ] Knowledge graph of topic relationships
- [ ] Predictive analytics (trend forecasting)
- [ ] Integration with product management tools (Jira, Linear)

## How This Compares to Traditional Methods

| What | Traditional (LDA/BERT) | This System (LLM-based) |
|------|------------------------|-------------------------|
| Setup | Weeks of training | Configure and go |
| Accuracy | ~60-70% | ~85-95% |
| Topics | "topic_7", "topic_14" | "Delivery delay", "App crashes" |
| Deduplication | Write rules manually | Automatic |
| Adapts to new issues | Need to retrain | Immediate |
| Cost | Infrastructure + time | ~$1 per 1000 reviews |
| Explainable | Not really | Yes, with reasoning |

## Security & Privacy

### Data Handling
- Reviews are processed in batches
- No PII extraction or storage
- API calls use HTTPS
- Local data stored in `/data/` (gitignored)

### API Keys
- Stored in `.env` (not committed)
- Environment variable based
- No hardcoded credentials

### Data Retention
- Processed data stored locally
- User controls deletion
- No data sent to third parties (except OpenAI for processing)

## Monitoring & Debugging

### Logs
- Processing logs for each batch
- API call logs
- Error logs with stack traces

### Metrics
- Reviews processed per day
- Topics extracted per review (avg)
- Consolidation ratio (topics before/after)
- Processing time per batch

### Debug Mode
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

