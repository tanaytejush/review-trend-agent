import unittest

from agents.topic_consolidation_agent import TopicConsolidationAgent


class TopicConsolidationTests(unittest.TestCase):
    def test_canonical_topic_maps_to_itself(self):
        agent = TopicConsolidationAgent.__new__(TopicConsolidationAgent)
        agent.topic_taxonomy = {}

        agent._update_taxonomy({
            "consolidated_topics": [{
                "canonical_name": "Delivery delay",
                "variants": ["Late delivery"],
            }]
        })

        self.assertEqual(agent.map_to_canonical("Late delivery"), "Delivery delay")
        self.assertEqual(agent.map_to_canonical("Delivery delay"), "Delivery delay")


if __name__ == "__main__":
    unittest.main()
