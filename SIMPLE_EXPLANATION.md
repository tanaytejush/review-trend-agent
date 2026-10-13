# Review Trend Agent: Simple Explanation

## In one sentence

This project reads app-store reviews and tells a product team which customer
problems are common, which problems are getting worse, and what customers are
asking for.

## Why is it needed?

An app can receive hundreds or thousands of reviews. A person cannot reliably
read all of them every day. The same problem is also described in many ways:

- "The delivery was late."
- "My order arrived very slowly."
- "Delivery time is terrible."

A simple keyword search may treat these as different issues. This project
understands that they are related and groups them under a single topic such as
**Delivery delay**.

## How it works

### 1. Collect reviews

The scraper gets reviews from a Google Play application and groups them by
date.

### 2. Understand each review

The language model reads small batches of reviews and identifies:

- Topics or problems.
- Whether the review is positive, negative, or neutral.
- A short explanation for the classification.

### 3. Combine duplicate topics

The consolidation agent creates a canonical name for similar topics. This
prevents the final report from splitting one real problem across many labels.

### 4. Count topics over time

The processor counts how often each canonical topic appears on each day.
Missing dates are represented as zero, which makes the data suitable for
trend charts and spreadsheets.

### 5. Create reports

The report generator produces:

- **CSV:** easy to open in Excel or import into another system.
- **JSON:** useful for APIs and automation.
- **Excel:** convenient for business analysis.
- **Summary JSON:** top topics, growing topics, and newly appearing topics.

## Example business question

Instead of asking:

> "Can someone read all of this month's reviews?"

the team can ask:

> "Which customer problems are increasing this week?"

The report can show that **Delivery partner rude** increased by 25% and
**Food arrived cold** is one of the most frequently mentioned issues. The
operations team can then investigate those areas first.

## Who benefits?

- **Product teams:** discover bugs, feature requests, and recurring
  complaints.
- **Operations teams:** identify service and delivery problems.
- **Customer support teams:** understand repeated customer pain points.
- **Managers:** receive a measurable summary instead of anecdotes.

## What this project is not

It is not a customer-support chatbot and it does not automatically fix
product issues. It is an analysis pipeline that turns customer language into
structured evidence for people who make product and operational decisions.

## Basic run

1. Install the dependencies.
2. Copy `.env.example` to `.env`.
3. Add an OpenAI API key.
4. Run:

```bash
python main.py --package com.application.zomato
```

5. Open the generated files in `output/`.
