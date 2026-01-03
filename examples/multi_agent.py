#!/usr/bin/env python3
"""
Multi-Agent Orchestration Example
==================================

Demonstrates consensus gating across multiple AI models.
When models disagree, silence is preferred over synthetic agreement.

Usage:
    python examples/multi_agent.py

This example demonstrates:
    - Calling multiple models in parallel
    - Measuring consensus across responses
    - Applying consensus gate
    - Handling disagreement with silence
"""

from typing import List, Optional, Callable
from silence_as_control import (
    SILENCE,
    CONSENSUS_THRESHOLD,
    gated_orchestration,
    measure_consensus,
    consensus_gate,
)


# =============================================================================
# MOCK MODELS (replace with real API calls in production)
# =============================================================================

def mock_gpt4(query: str) -> str:
    """Mock GPT-4 responses."""
    responses = {
        "capital": "The capital of Australia is Canberra.",
        "math": "2 + 2 = 4",
        "philosophy": "Consciousness likely emerges from complex neural processes.",
        "uncertain": "I believe the answer is approximately 42.",
    }
    for key, response in responses.items():
        if key in query.lower():
            return response
    return f"GPT-4 response: {query[:30]}"


def mock_claude(query: str) -> str:
    """Mock Claude responses."""
    responses = {
        "capital": "Canberra is the capital of Australia.",
        "math": "The answer is 4.",
        "philosophy": "We cannot definitively know if consciousness is computable.",
        "uncertain": "I'm uncertain, but perhaps around 40-45.",
    }
    for key, response in responses.items():
        if key in query.lower():
            return response
    return f"Claude response: {query[:30]}"


def mock_grok(query: str) -> str:
    """Mock Grok responses."""
    responses = {
        "capital": "Canberra, founded in 1913, is Australia's capital.",
        "math": "4, obviously!",
        "philosophy": "Consciousness is probably not computable in the classical sense.",
        "uncertain": "Wild guess: 37.",
    }
    for key, response in responses.items():
        if key in query.lower():
            return response
    return f"Grok response: {query[:30]}"


# =============================================================================
# ORCHESTRATION
# =============================================================================

class MultiModelOrchestrator:
    """
    Orchestrates multiple AI models with consensus gating.

    When models agree → returns aggregated response
    When models disagree → returns SILENCE
    """

    def __init__(
        self,
        models: List[Callable[[str], str]],
        consensus_threshold: float = CONSENSUS_THRESHOLD,
        aggregation: str = "first",  # "first", "majority", "longest"
    ):
        """
        Initialize orchestrator.

        Args:
            models: List of model functions (query) -> response
            consensus_threshold: Minimum consensus required
            aggregation: How to aggregate when consensus passes
        """
        self.models = models
        self.consensus_threshold = consensus_threshold
        self.aggregation = aggregation
        self.stats = {
            "queries": 0,
            "agreements": 0,
            "silences": 0,
        }

    def query(self, prompt: str) -> Optional[str]:
        """
        Query all models and apply consensus gate.

        Returns aggregated response or SILENCE.
        """
        self.stats["queries"] += 1

        # Get responses from all models
        responses = [model(prompt) for model in self.models]

        # Measure consensus
        consensus = self._measure_semantic_consensus(responses)

        print(f"  📊 Consensus score: {consensus:.2f}")
        for i, response in enumerate(responses):
            print(f"     Model {i+1}: {response[:50]}...")

        # Apply gate
        if consensus_gate(consensus, self.consensus_threshold):
            self.stats["silences"] += 1
            return SILENCE

        self.stats["agreements"] += 1
        return self._aggregate(responses)

    def _measure_semantic_consensus(self, responses: List[str]) -> float:
        """
        Measure semantic consensus (not just string equality).

        In production, use embedding similarity.
        """
        if not responses:
            return 0.0

        # Normalize responses for comparison
        normalized = [r.lower().strip() for r in responses]

        # Check for key phrase agreement
        # Extract potential "answer" patterns
        agreements = 0
        total_pairs = 0

        for i in range(len(normalized)):
            for j in range(i + 1, len(normalized)):
                total_pairs += 1

                # Check for common significant words
                words_i = set(normalized[i].split())
                words_j = set(normalized[j].split())

                # Remove common stop words
                stop_words = {"the", "a", "is", "are", "of", "to", "in", "that", "it"}
                words_i -= stop_words
                words_j -= stop_words

                if len(words_i) == 0 or len(words_j) == 0:
                    continue

                # Jaccard similarity
                intersection = len(words_i & words_j)
                union = len(words_i | words_j)
                similarity = intersection / union if union > 0 else 0

                if similarity > 0.3:  # Threshold for "similar enough"
                    agreements += 1

        if total_pairs == 0:
            return 1.0

        return agreements / total_pairs

    def _aggregate(self, responses: List[str]) -> str:
        """Aggregate responses when consensus passes."""
        if self.aggregation == "first":
            return responses[0]
        elif self.aggregation == "longest":
            return max(responses, key=len)
        elif self.aggregation == "majority":
            # Find most common response pattern
            from collections import Counter
            normalized = [r.lower()[:50] for r in responses]
            most_common = Counter(normalized).most_common(1)[0][0]
            for r in responses:
                if r.lower().startswith(most_common[:20]):
                    return r
            return responses[0]
        return responses[0]

    def get_stats(self) -> dict:
        """Get orchestration statistics."""
        total = self.stats["queries"]
        return {
            **self.stats,
            "silence_rate": self.stats["silences"] / total if total > 0 else 0,
            "agreement_rate": self.stats["agreements"] / total if total > 0 else 0,
        }


# =============================================================================
# DEMO
# =============================================================================

def run_demo():
    """Run multi-model orchestration demo."""
    print("=" * 70)
    print("Multi-Model Orchestration with Consensus Gating")
    print("=" * 70)
    print()
    print("This demo queries 3 models (GPT-4, Claude, Grok) and applies")
    print("consensus gating. If models disagree → SILENCE.")
    print()

    # Initialize orchestrator with 3 models
    orchestrator = MultiModelOrchestrator(
        models=[mock_gpt4, mock_claude, mock_grok],
        consensus_threshold=0.5,
    )

    # Test scenarios
    scenarios = [
        ("What is the capital of Australia?", "Factual - should agree"),
        ("What is 2 + 2? (math)", "Simple math - should agree"),
        ("Is consciousness computable? (philosophy)", "Philosophical - may disagree"),
        ("What's the answer to life? (uncertain)", "Uncertain - likely disagree"),
    ]

    print("-" * 70)

    for query, description in scenarios:
        print(f"\n🔍 {description}")
        print(f"   Query: \"{query}\"")
        print()

        result = orchestrator.query(query)

        if result is SILENCE:
            print(f"\n   🤫 Result: [SILENCE]")
            print("   → Models disagreed, no synthetic consensus forced")
        else:
            print(f"\n   ✅ Result: {result}")

        print("-" * 70)

    # Print final stats
    stats = orchestrator.get_stats()
    print(f"\n📊 Final Statistics:")
    print(f"   Total Queries: {stats['queries']}")
    print(f"   Agreements: {stats['agreements']} ({stats['agreement_rate']:.0%})")
    print(f"   Silences: {stats['silences']} ({stats['silence_rate']:.0%})")


def run_interactive():
    """Run interactive multi-model query."""
    print("=" * 70)
    print("Interactive Multi-Model Query")
    print("=" * 70)
    print()
    print("Enter queries to test consensus across GPT-4, Claude, and Grok.")
    print("Type /quit to exit, /stats for statistics.")
    print()

    orchestrator = MultiModelOrchestrator(
        models=[mock_gpt4, mock_claude, mock_grok],
        consensus_threshold=0.5,
    )

    while True:
        try:
            query = input("\nYour query: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if query.lower() == "/quit":
            break

        if query.lower() == "/stats":
            print(f"📊 Stats: {orchestrator.get_stats()}")
            continue

        if not query:
            continue

        print()
        result = orchestrator.query(query)

        if result is SILENCE:
            print(f"\n🤫 [SILENCE] - Models disagreed")
        else:
            print(f"\n✅ Consensus: {result}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive()
    else:
        run_demo()
