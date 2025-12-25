"""Configuration management for the review trend analysis agent."""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# App Configuration
APP_PACKAGE_NAME = os.getenv("APP_PACKAGE_NAME", "com.application.zomato")
APP_STORE = os.getenv("APP_STORE", "google_play")
START_DATE = datetime.strptime(os.getenv("START_DATE", "2024-06-01"), "%Y-%m-%d")

# Agent Configuration
TOPIC_EXTRACTION_MODEL = os.getenv("TOPIC_EXTRACTION_MODEL", "gpt-4-turbo-preview")
TOPIC_CONSOLIDATION_MODEL = os.getenv("TOPIC_CONSOLIDATION_MODEL", "gpt-4-turbo-preview")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Seed Topics (for food delivery apps)
SEED_TOPICS = [
    "Delivery issue",
    "Food quality - stale/bad",
    "Delivery partner behavior",
    "App technical issues",
    "Payment problems",
    "Customer service",
    "Pricing and offers",
    "Order accuracy",
    "Restaurant quality",
    "Delivery time"
]

# Report Configuration
TREND_WINDOW_DAYS = 31  # T to T-30 (31 days total)
