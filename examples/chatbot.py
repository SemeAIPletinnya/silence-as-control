#!/usr/bin/env python3
"""
Chatbot Example with Silence-as-Control
========================================

A simple chatbot that uses silence gating to avoid low-coherence responses.

Usage:
    python examples/chatbot.py

This example demonstrates:
    - Using SilenceGatedAgent for conversation
    - Handling silence responses gracefully
    - Tracking silence statistics
"""

from silence_as_control import SilenceGatedAgent, SILENCE


def mock_llm(context: list, query: str) -> str:
    """
    Mock LLM function for demonstration.

    In production, replace with actual LLM call:
    - OpenAI: openai.ChatCompletion.create(...)
    - Anthropic: anthropic.messages.create(...)
    - Local: ollama.chat(...)
    """
    # Simple echo with context awareness
    if not context:
        return f"Hello! You asked: {query}"

    # Simulate lower coherence for certain queries
    if "?" in query and len(query) > 50:
        # Complex questions might trigger lower coherence
        return f"I'm not entirely sure, but... {query[:20]}..."

    return f"Based on our conversation, here's my response to: {query}"


def custom_coherence(context: list, response: str) -> float:
    """
    Custom coherence function.

    In production, implement using:
    - Embedding similarity (sentence-transformers)
    - Self-consistency sampling
    - Model confidence scores
    """
    # Heuristic: responses with "not sure" = lower coherence
    if "not sure" in response.lower() or "uncertain" in response.lower():
        return 0.5  # Below default threshold of 0.7

    # Heuristic: very short responses = potentially low coherence
    if len(response) < 10:
        return 0.4

    # Default: assume reasonable coherence
    return 0.85


def custom_drift(context: list, history: list) -> float:
    """
    Custom drift function.

    Drift accumulates over conversation length.
    Longer conversations = higher drift risk.
    """
    # Accumulate drift based on history length
    base_drift = min(len(history) * 0.03, 0.25)

    # Check for topic shifts (simplified)
    if len(history) >= 4:
        recent = " ".join(history[-2:]).lower()
        older = " ".join(history[-4:-2]).lower()

        # Very basic topic shift detection
        common_words = set(recent.split()) & set(older.split())
        if len(common_words) < 3:
            base_drift += 0.1  # Topic shift penalty

    return min(base_drift, 0.5)


def run_chatbot():
    """Run the silence-gated chatbot."""
    print("=" * 60)
    print("Silence-as-Control Chatbot Demo")
    print("=" * 60)
    print()
    print("This chatbot uses coherence gating.")
    print("If it's uncertain, it will remain SILENT instead of guessing.")
    print()
    print("Commands:")
    print("  /stats  - Show silence statistics")
    print("  /reset  - Reset conversation")
    print("  /quit   - Exit")
    print()
    print("-" * 60)

    # Initialize agent with custom functions
    agent = SilenceGatedAgent(
        model_fn=mock_llm,
        coherence_fn=custom_coherence,
        drift_fn=custom_drift,
        coherence_threshold=0.7,
        drift_threshold=0.3,
    )

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.lower() == "/quit":
            print("Goodbye!")
            break

        if user_input.lower() == "/stats":
            stats = agent.get_stats()
            print("\n📊 Statistics:")
            print(f"   Responses: {stats['responses']}")
            print(f"   Silences:  {stats['silences']}")
            print(f"   Silence Rate: {stats['silence_rate']:.1%}")
            print(f"   History Length: {stats['history_length']}")
            continue

        if user_input.lower() == "/reset":
            agent.reset()
            print("🔄 Conversation reset.")
            continue

        # Get response with silence gating
        response = agent.step(user_input)

        if response is SILENCE:
            print("\n🤫 Bot: [SILENCE]")
            print("   (The bot chose not to respond due to low coherence)")
        else:
            print(f"\n🤖 Bot: {response}")


def demo_silence_scenarios():
    """Demonstrate different silence scenarios."""
    print("\n" + "=" * 60)
    print("Silence Scenarios Demo")
    print("=" * 60)

    agent = SilenceGatedAgent(
        model_fn=mock_llm,
        coherence_fn=custom_coherence,
        drift_fn=custom_drift,
    )

    scenarios = [
        ("Hello!", "Normal greeting"),
        ("Hi there", "Another greeting"),
        ("Tell me about quantum physics", "Normal question"),
        (
            "What if consciousness is actually a quantum phenomenon that emerges from the collapse of wave functions in neural microtubules?",
            "Complex uncertain question",
        ),
        ("k", "Too short response trigger"),
    ]

    for query, description in scenarios:
        print(f"\n📝 Scenario: {description}")
        print(f"   Query: {query[:50]}...")

        response = agent.step(query)

        if response is SILENCE:
            print("   Response: 🤫 [SILENCE]")
        else:
            print(f"   Response: {response[:50]}...")

    print(f"\n📊 Final Stats: {agent.get_stats()}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_silence_scenarios()
    else:
        run_chatbot()
