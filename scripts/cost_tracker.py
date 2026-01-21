#!/usr/bin/env python3
"""
Cost tracking utility for Anthropic API usage.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Pricing per 1M tokens (as of 2024)
PRICING = {
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-haiku-3-5-20241022": {"input": 0.25, "output": 1.25},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for a given API call."""
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model}")

    pricing = PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return input_cost + output_cost


def log_usage(model: str, input_tokens: int, output_tokens: int,
              customer_id: str = "default") -> dict:
    """Log API usage and return cost details."""
    cost = calculate_cost(model, input_tokens, output_tokens)

    usage = {
        "timestamp": datetime.utcnow().isoformat(),
        "customer_id": customer_id,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
    }

    return usage


if __name__ == "__main__":
    # Example usage
    example = log_usage(
        model="claude-sonnet-4-20250514",
        input_tokens=1000,
        output_tokens=500,
        customer_id="example-customer"
    )
    print(f"Example usage: {example}")
