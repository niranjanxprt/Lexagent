"""
Initialize Langfuse prompts for LexAgent.
Run this once to create all prompts in Langfuse.

Usage:
    uv run python app/init_langfuse_prompts.py
"""

from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()

langfuse = get_client()

# Define all LexAgent prompts
PROMPTS = [
    {
        "name": "legal-research/generate-plan",
        "type": "chat",
        "prompt": [
            {
                "role": "system",
                "content": (
                    "You are a senior legal research assistant. "
                    "Given a legal research goal, produce a list of 3 to 6 specific "
                    "research tasks needed to fully answer the question. "
                    "Each task must specify what to search for and why it matters. "
                    "Return ONLY a valid JSON object in this exact format:\n"
                    '{"tasks": [{"title": "...", "description": "..."}, ...]}'
                ),
            },
            {"role": "user", "content": "Legal research goal: {{goal}}"},
        ],
        "labels": ["production"],
    },
    {
        "name": "legal-research/refine-query",
        "type": "chat",
        "prompt": [
            {
                "role": "system",
                "content": (
                    "You are a legal research assistant. "
                    "Given a task and prior research context, write a precise "
                    "web search query (max 12 words) to find the most relevant "
                    "legal information. Return ONLY the query string."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Task: {{task_title}}\n"
                    "Description: {{task_description}}\n"
                    "Prior context:\n{{context_notes}}"
                ),
            },
        ],
        "labels": ["production"],
    },
    {
        "name": "legal-research/compress-results",
        "type": "chat",
        "prompt": [
            {
                "role": "system",
                "content": (
                    "You are a legal research assistant. "
                    "Compress the following search results into exactly 2-3 sentences "
                    "that capture the most legally relevant findings. "
                    "Be precise and cite the source titles in parentheses."
                ),
            },
            {
                "role": "user",
                "content": "Task: {{task_title}}\n\nSearch results:\n{{search_results}}",
            },
        ],
        "labels": ["production"],
    },
    {
        "name": "legal-research/reflect",
        "type": "chat",
        "prompt": [
            {
                "role": "system",
                "content": (
                    "You are a legal research QA reviewer. "
                    "Given a task description and its compressed findings, "
                    "write 1 sentence evaluating whether the task was adequately answered "
                    "and what (if anything) remains unclear."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Task: {{task_description}}\n\n" "Findings: {{findings}}"
                ),
            },
        ],
        "labels": ["production"],
    },
    {
        "name": "legal-research/generate-report",
        "type": "chat",
        "prompt": [
            {
                "role": "system",
                "content": (
                    "You are a senior legal analyst. "
                    "Using the research notes below, write a comprehensive, "
                    "well-structured legal research report in Markdown. "
                    "Include: Executive Summary, Key Findings per topic, "
                    "Legal Implications, Limitations, and Conclusion."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Research Goal: {{goal}}\n\n"
                    "Task Summaries:\n{{task_summaries}}\n\n"
                    "Detailed Research Notes:\n{{context_notes}}"
                ),
            },
        ],
        "labels": ["production"],
    },
]


def init_prompts():
    """Create all LexAgent prompts in Langfuse."""
    print("\n" + "=" * 70)
    print("🚀 Initializing LexAgent Prompts in Langfuse")
    print("=" * 70 + "\n")

    for prompt_config in PROMPTS:
        try:
            langfuse.create_prompt(**prompt_config)
            print(f"✅ Created: {prompt_config['name']}")
        except Exception as e:
            print(f"❌ Failed to create {prompt_config['name']}: {e}")

    print("\n" + "=" * 70)
    print("✅ Prompt initialization complete!")
    print("=" * 70)
    print("\nPrompts are now managed in Langfuse.")
    print("Non-technical team members can update them without code changes.")
    print("\nTo use in production:")
    print("  1. Visit your Langfuse dashboard")
    print("  2. Go to Prompt Management")
    print("  3. Edit prompts as needed")
    print("  4. Label new versions with 'production' to deploy")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    init_prompts()
