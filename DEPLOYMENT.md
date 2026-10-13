# Deployment

## Quick Start

### Docker (easiest)

```bash
docker build -t review-trend-agent .
docker run -e OPENAI_API_KEY=your_key review-trend-agent --package com.application.zomato
```

### Manual Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
python main.py
```

## For Production

### What You Need
- Python 3.8+
- At least 2GB RAM
- Disk space for data
- Internet connection

### Environment Variables

Required:
- `OPENAI_API_KEY`

Optional (see .env.example for more):
- `APP_PACKAGE_NAME`
- `START_DATE`
- `TOPIC_EXTRACTION_MODEL`
- `TEMPERATURE`

### Running Daily (cron)

```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/review-trend-agent && python main.py
```

### Monitoring
- Check logs
- Watch API usage in OpenAI dashboard
- Review reports in `output/`

### If Things Go Wrong

**High costs?**
- Use caching
- Switch to gpt-3.5-turbo
- Process less frequently

**Running slow?**
- Increase batch sizes
- Check your internet connection

**Out of memory?**
- Process smaller date ranges
- Add more RAM

## More Info

See README.md for basics, ARCHITECTURE.md for how it works.
