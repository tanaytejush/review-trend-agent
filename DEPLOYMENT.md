# Deployment Guide

## Quick Deployment

### Using Docker (Recommended)

1. Build the image:
```bash
docker build -t review-trend-agent .
```

2. Run the container:
```bash
docker run -e OPENAI_API_KEY=your_key review-trend-agent \
  --package com.application.zomato
```

### Manual Deployment

1. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
export OPENAI_API_KEY=your_key
export APP_PACKAGE_NAME=com.application.zomato
```

3. Run the application:
```bash
python main.py
```

## Production Deployment

### Requirements

- Python 3.8+
- 2GB RAM minimum
- Disk space for review data storage
- Internet connection for API access

### Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key

Optional:
- `APP_PACKAGE_NAME`: Default app to analyze
- `START_DATE`: Default start date (YYYY-MM-DD)
- `TOPIC_EXTRACTION_MODEL`: Model for extraction
- `TOPIC_CONSOLIDATION_MODEL`: Model for consolidation
- `TEMPERATURE`: Model temperature (0.0-1.0)
- `MAX_RETRIES`: Number of retry attempts

### Scheduling

Set up cron job for daily runs:
```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/review-trend-agent && python main.py
```

### Monitoring

- Check logs in standard output
- Monitor API usage in OpenAI dashboard
- Review generated reports in `output/` directory

### Scaling

For high volume:
- Increase batch sizes
- Use multiple workers
- Implement request queuing
- Cache results aggressively

## Security

- Store API keys securely (use secrets manager)
- Restrict file system access
- Enable rate limiting
- Monitor for unusual patterns

## Troubleshooting

### High API Costs

- Reduce batch frequency
- Use caching
- Optimize model selection

### Slow Performance

- Increase batch sizes
- Use parallel processing
- Check network latency

### Out of Memory

- Process smaller date ranges
- Implement streaming
- Increase system RAM

## Support

For deployment issues, refer to:
- README.md for basic setup
- GETTING_STARTED.md for detailed instructions
- ARCHITECTURE.md for system design
