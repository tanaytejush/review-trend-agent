"""Agentic AI system for consolidating and deduplicating similar topics."""

import json
from typing import List, Dict, Tuple
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config.config import (
    OPENAI_API_KEY,
    TOPIC_CONSOLIDATION_MODEL,
    TEMPERATURE,
    MAX_RETRIES
)


class TopicConsolidationAgent:
    """LLM-based agent for consolidating similar topics into canonical forms.

    This agent solves the key challenge: similar but not identical topics being
    created as different categories (e.g., "delivery guy rude" vs "delivery partner
    impolite" vs "delivery person behaved badly").
    """

    def __init__(self, model: str = TOPIC_CONSOLIDATION_MODEL):
        """Initialize the consolidation agent.

        Args:
            model: OpenAI model to use
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model
        self.topic_taxonomy = {}  # Maps variant topics to canonical topics

    def _create_consolidation_prompt(self, topics: List[str]) -> str:
        """Create prompt for topic consolidation.

        Args:
            topics: List of topic strings to consolidate

        Returns:
            Formatted prompt string
        """
        topics_text = "\n".join([f"- {topic}" for topic in topics])

        prompt = f"""You are an expert at creating taxonomies and ontologies for customer feedback analysis.

Your task is to analyze the following topics extracted from app reviews and consolidate similar/duplicate topics into canonical forms.

TOPICS TO CONSOLIDATE:
{topics_text}

GUIDELINES:
1. Group semantically similar topics together
2. Choose the clearest, most concise canonical name for each group
3. Topics with different meanings should NOT be merged (e.g., "late delivery" ≠ "missing delivery")
4. Consider synonyms, paraphrases, and different phrasings of the same issue
5. Maintain specific details when topics are genuinely different

Examples of consolidation:
- "Delivery guy rude", "Delivery partner impolite", "Delivery person behaved badly" → "Delivery partner rude"
- "App crashes", "App keeps freezing", "Application not working" → "App crashes/freezing"
- "Food was cold", "Food arrived cold", "Cold food delivery" → "Food arrived cold"

Return a JSON object with this structure:
{{
  "consolidated_topics": [
    {{
      "canonical_name": "The main topic name to use",
      "variants": ["list", "of", "similar", "topics", "that", "map", "to", "this"],
      "description": "Brief explanation of what this topic covers",
      "category": "issue|request|feedback|praise"
    }}
  ],
  "reasoning": "Explanation of your consolidation decisions"
}}

Return ONLY the JSON object, no additional text."""

        return prompt

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def consolidate_topics(self, topics: List[str]) -> Dict[str, any]:
        """Consolidate similar topics into canonical forms.

        Args:
            topics: List of topic strings to consolidate

        Returns:
            Dictionary with consolidated topics and mapping
        """
        # Remove duplicates and sort
        unique_topics = sorted(list(set(topics)))

        if len(unique_topics) <= 1:
            return {
                "consolidated_topics": [
                    {
                        "canonical_name": unique_topics[0] if unique_topics else "",
                        "variants": unique_topics,
                        "description": "",
                        "category": "issue"
                    }
                ] if unique_topics else [],
                "reasoning": "Only one or zero topics to consolidate"
            }

        try:
            prompt = self._create_consolidation_prompt(unique_topics)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at topic taxonomy and consolidation. Always return valid JSON."
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
            consolidation = json.loads(result)

            # Build taxonomy mapping
            self._update_taxonomy(consolidation)

            return consolidation

        except Exception as e:
            print(f"Error during consolidation: {e}")
            # Fallback: no consolidation
            return {
                "consolidated_topics": [
                    {
                        "canonical_name": topic,
                        "variants": [topic],
                        "description": "",
                        "category": "issue"
                    }
                    for topic in unique_topics
                ],
                "reasoning": f"Error occurred: {str(e)}"
            }

    def _update_taxonomy(self, consolidation: Dict):
        """Update internal taxonomy mapping.

        Args:
            consolidation: Consolidation result dictionary
        """
        for topic_group in consolidation.get('consolidated_topics', []):
            canonical = topic_group['canonical_name']
            variants = topic_group.get('variants', [])

            for variant in variants:
                self.topic_taxonomy[variant] = canonical

    def map_to_canonical(self, topic: str) -> str:
        """Map a topic to its canonical form.

        Args:
            topic: Topic string to map

        Returns:
            Canonical topic name
        """
        return self.topic_taxonomy.get(topic, topic)

    def get_taxonomy(self) -> Dict[str, str]:
        """Get the complete topic taxonomy mapping.

        Returns:
            Dictionary mapping variant topics to canonical topics
        """
        return self.topic_taxonomy.copy()

    def incremental_consolidation(
        self,
        new_topics: List[str],
        existing_canonical_topics: List[Dict]
    ) -> Tuple[List[Dict], List[str]]:
        """Incrementally consolidate new topics with existing ones.

        Args:
            new_topics: New topics to consolidate
            existing_canonical_topics: Existing consolidated topic groups

        Returns:
            Tuple of (updated_consolidated_topics, truly_new_topics)
        """
        # Extract existing canonical names
        existing_names = [t['canonical_name'] for t in existing_canonical_topics]

        # Combine with new topics
        all_topics = existing_names + new_topics

        # Consolidate
        consolidation = self.consolidate_topics(all_topics)

        # Identify truly new topics (not mapped to existing ones)
        truly_new = []
        for topic_group in consolidation.get('consolidated_topics', []):
            canonical = topic_group['canonical_name']
            if canonical not in existing_names:
                # Check if any variants were in the new topics
                variants_in_new = [v for v in topic_group.get('variants', []) if v in new_topics]
                if variants_in_new:
                    truly_new.append(canonical)

        return consolidation.get('consolidated_topics', []), truly_new


def main():
    """Test the topic consolidation agent."""
    # Sample topics with duplicates and similar meanings
    sample_topics = [
        "Delivery guy was rude",
        "Delivery partner behaved badly",
        "Delivery person was impolite",
        "Food arrived cold",
        "Food was stale",
        "Cold food delivery",
        "App crashes",
        "Application keeps freezing",
        "App not working properly",
        "Maps navigation issue",
        "Maps not working",
        "Please add 10 minute delivery",
        "Bring back bolt delivery",
        "Want faster delivery option"
    ]

    agent = TopicConsolidationAgent()
    consolidation = agent.consolidate_topics(sample_topics)

    print("Consolidated Topics:")
    print(json.dumps(consolidation, indent=2))

    print("\n\nTopic Taxonomy Mapping:")
    for variant, canonical in agent.get_taxonomy().items():
        print(f"  '{variant}' → '{canonical}'")


if __name__ == "__main__":
    main()
