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
                    "You're a senior legal research assistant helping break down a research goal into concrete steps. "
                    "Think of it like planning a short research memo: the user has one big question, and you're listing 3 to 6 "
                    "specific tasks (each something we can answer with a focused web search). For each task, say what to look for and why it matters. "
                    "Every task should be a research/search task — nothing that's just 'write' or 'compile'. "
                    "Do not add a final task like 'compile the report', 'synthesize findings', or 'write the final report': "
                    "the system generates the report automatically once all research tasks are done. "
                    "Reply with only a valid JSON object in this exact shape, no other text:\n"
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
                    "You're helping turn a research task into one short web search query (max 12 words). "
                    "Given the task and what we've already found, suggest a precise query that will surface the most relevant legal material. "
                    "Prefer wording that leads to authoritative sources — think official databases (eur-lex, gesetze-im-internet.de, regulators) rather than blogs. "
                    "Reply with only the query itself: no explanation, no quotation marks, no preamble. Do not add sentences like 'Here is the query' or 'You could search for'."
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
                    "You're summarizing search results for a legal research memo. In 2–3 sentences, capture what matters most for the question at hand. "
                    "Keep article and section references exactly as they appear — e.g. 'GDPR Article 5', 'BDSG §26' — do not paraphrase or renumber them. "
                    "Mention the source (in parentheses) so we can trace back. Do not add anything that wasn't in the search results; stick to what's there."
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
                    "You're doing a quick QA check on the research we just did. In one sentence: did we answer the task, or is something important missing? "
                    "If we're good, say so clearly (e.g. 'This task was fully addressed.'). "
                    "If not, say what's still missing in one short clause. Do not repeat the findings; only judge completeness and name the gap if there is one."
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
                    "You're drafting a legal research report for the reader. Use the research notes below to build a clear, structured Markdown report. "
                    "Include: Executive Summary, Key Findings (by topic), Legal Implications, Limitations, and Conclusion. "
                    "End with a Sources section: list the key URLs from the notes so the reader can follow up. "
                    "When you refer to law, cite it explicitly (e.g. 'Under GDPR Article 25…' or 'BDSG §26 provides…'). "
                    "Do not invent articles or sources that aren't in the notes; only use what the research actually found."
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
