#!/usr/bin/env python3
"""Quick start example for Claude Code SDK."""

import anyio
from claude_code_sdk import (
    AssistantMessage,
    ClaudeCodeOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def with_tools_example():
    """Example using tools."""
    print("=== With Tools Example ===")

    options = ClaudeCodeOptions(allowed_tools=["Read", "Write"])

    async for message in query(
        prompt="Create a survival analysis app in app.R, with modules: tm_g_forest_tte, tm_t_tte, tm_g_km, tm_t_coxreg",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage) and message.total_cost_usd > 0:
            print(f"\nCost: ${message.total_cost_usd:.4f}")
    print()


async def main():
    """Run all examples."""
    await with_tools_example()


if __name__ == "__main__":
    anyio.run(main)
