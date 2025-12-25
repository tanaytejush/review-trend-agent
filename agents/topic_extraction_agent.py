"""Topic extraction module using natural language processing."""

import json
from typing import List, Dict, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config.config import (
    OPENAI_API_KEY,
    TOPIC_EXTRACTION_MODEL,
    TEMPERATURE,
    MAX_RETRIES,
    SEED_TOPICS
)


class TopicExtractionAgent:
    """Extracts topics from app reviews using language models."""

    def __init__(self, model: str = TOPIC_EXTRACTION_MODEL):
        """Initialize the agent.

        Args:
            model: OpenAI model to use
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.seed_topics = SEED_TOPICS

    def _create_extraction_prompt(self, reviews: List[str], existing_topics: List[str]) -> str:
        """Create prompt for topic extraction.

        Args:
            reviews: List of review texts
            existing_topics: List of already identified topics

        Returns:
            Formatted prompt string
        """
        reviews_text = "\n".join([f"{i+1}. {review}" for i, review in enumerate(reviews)])

        prompt = f"""You are an expert at analyzing customer feedback for food delivery applications.

Your task is to analyze the following customer reviews and extract the main topics, issues, requests, or feedback mentioned.

EXISTING TOPICS (reference these when applicable):
{json.dumps(existing_topics, indent=2)}

GUIDELINES:
1. Identify specific, actionable topics from the reviews
2. Use existing topics when the review matches them
3. Create new topics only when reviews discuss something not covered by existing topics
4. Topics should be concise (3-7 words max)
5. Focus on: issues, feature requests, complaints, praise, and suggestions
6. Categorize similar complaints under the same topic

REVIEWS:
{reviews_text}

Return a JSON array where each element has:
- "review_index": the review number (1-based)
- "topics": array of topic strings identified in that review
- "sentiment": "positive", "negative", or "neutral"
- "reasoning": brief explanation of why these topics were chosen

Example output format:
[
  {{
    "review_index": 1,
    "topics": ["Delivery delay", "Cold food"],
    "sentiment": "negative",
    "reasoning": "Customer complained about late delivery and food arriving cold"
  }}
]

Return ONLY the JSON array, no additional text."""

        return prompt

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def extract_topics(
        self,
        reviews: List[Dict],
        batch_size: int = 10,
        existing_topics: Optional[List[str]] = None
    ) -> List[Dict]:
        """Extract topics from reviews using LLM.

        Args:
            reviews: List of review dictionaries with 'content' field
            batch_size: Number of reviews to process in one API call
            existing_topics: List of previously identified topics

        Returns:
            List of dictionaries with extracted topics for each review
        """
        if existing_topics is None:
            existing_topics = self.seed_topics.copy()

        all_extractions = []

        # Process reviews in batches
        for i in range(0, len(reviews), batch_size):
            batch = reviews[i:i + batch_size]
            review_texts = [r.get('content', '') for r in batch]

            # Skip empty reviews
            review_texts = [text for text in review_texts if text.strip()]

            if not review_texts:
                continue

            try:
                prompt = self._create_extraction_prompt(review_texts, existing_topics)

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at analyzing customer feedback and extracting topics. Always return valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=TEMPERATURE,
                    response_format={"type": "json_object"}
                )

                result = response.choices[0].message.content
                extractions = json.loads(result)

                # Handle both array and object with array inside
                if isinstance(extractions, dict) and 'extractions' in extractions:
                    extractions = extractions['extractions']
                elif isinstance(extractions, dict) and 'topics' in extractions:
                    extractions = extractions['topics']

                # Add original review data
                for j, extraction in enumerate(extractions):
                    if j < len(batch):
                        extraction['review_id'] = batch[j].get('review_id')
                        extraction['review_content'] = batch[j].get('content')
                        extraction['review_date'] = batch[j].get('date')
                        extraction['review_score'] = batch[j].get('score')

                all_extractions.extend(extractions)

                # Update existing topics with new ones found
                for extraction in extractions:
                    for topic in extraction.get('topics', []):
                        if topic not in existing_topics:
                            existing_topics.append(topic)

            except json.JSONDecodeError as e:
                print(f"JSON decode error in batch {i}: {e}")
                continue
            except Exception as e:
                print(f"Error processing batch {i}: {e}")
                continue

        return all_extractions

    def get_all_unique_topics(self, extractions: List[Dict]) -> List[str]:
        """Get all unique topics from extractions.

        Args:
            extractions: List of extraction dictionaries

        Returns:
            List of unique topic strings
        """
        all_topics = set()

        for extraction in extractions:
            topics = extraction.get('topics', [])
            all_topics.update(topics)

        return sorted(list(all_topics))


def main():
    """Test the topic extraction agent."""
    # Sample reviews for testing
    sample_reviews = [
        {
            "review_id": "1",
            "content": "Delivery guy was extremely rude and threw the food at my door",
            "date": "2024-06-01",
            "score": 1
        },
        {
            "review_id": "2",
            "content": "Food arrived completely cold and stale. Waste of money!",
            "date": "2024-06-01",
            "score": 1
        },
        {
            "review_id": "3",
            "content": "The app keeps crashing when I try to apply coupon codes",
            "date": "2024-06-01",
            "score": 2
        },
        {
            "review_id": "4",
            "content": "Delivery was super fast! Food was hot and delicious",
            "date": "2024-06-01",
            "score": 5
        },
        {
            "review_id": "5",
            "content": "Please bring back the 10 minute delivery option, it was so convenient",
            "date": "2024-06-01",
            "score": 3
        }
    ]

    agent = TopicExtractionAgent()
    extractions = agent.extract_topics(sample_reviews)

    print("Topic Extractions:")
    print(json.dumps(extractions, indent=2))

    print("\n\nUnique Topics Found:")
    unique_topics = agent.get_all_unique_topics(extractions)
    for topic in unique_topics:
        print(f"  - {topic}")


if __name__ == "__main__":
    main()
