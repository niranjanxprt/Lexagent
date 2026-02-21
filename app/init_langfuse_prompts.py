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
                    "You are a senior legal research planner. Break the user's legal research goal into 3 to 6 independently web-searchable research tasks.\n\n"
                    "Output contract:\n"
                    "- Return ONLY valid JSON with no markdown, no code fences, and no prose.\n"
                    '- Exact schema: {"tasks":[{"title":"...","description":"..."}, ...]}\n'
                    "- If you cannot fully satisfy constraints, still return your best attempt in valid JSON with this exact schema.\n\n"
                    "Each task must:\n"
                    "- Focus on legal substance: statutes, regulations, official guidance, case law, or regulator enforcement practice.\n"
                    "- Be narrow enough to answer with one focused web search.\n"
                    "- State what to find and why it matters.\n"
                    "- Prefer primary/official sources first: official law portals, courts, regulators, EUR-Lex, Bundesjustizministerium before blogs.\n\n"
                    "Jurisdiction rule:\n"
                    "- If jurisdiction is not specified, include one task to identify applicable jurisdiction and governing legal framework first.\n\n"
                    "Do not add any task that writes, compiles, or synthesizes findings; report generation is automatic."
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
                    "Return exactly one web search query (max 12 words) that is most likely to retrieve authoritative legal sources for this task.\n\n"
                    "Output contract:\n"
                    "- Return one line only: the query text.\n"
                    "- No quotes, no prefix, no suffix, no explanation, no trailing period.\n\n"
                    "Query rules:\n"
                    "- Include discriminative legal terms: jurisdiction, law name, article/section number, topic.\n"
                    "- Prioritize primary sources: official law portals, courts, regulators, EUR-Lex, gesetze-im-internet.de.\n"
                    "- Use prior context only to resolve ambiguity, not to broaden scope."
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
                    "Summarize the search results into 2 to 4 sentences for a legal research memo.\n\n"
                    "Rules:\n"
                    "- Ground every claim in provided search results only; do not introduce outside knowledge.\n"
                    "- Preserve legal citations exactly as written (for example: GDPR Article 5, BDSG §26, EU AI Act Article 9).\n"
                    "- Include attribution for each key point in parentheses with source name and URL when present.\n"
                    "- If multiple sources agree, cite the most authoritative source.\n"
                    '- If sources conflict or evidence is weak/secondary, state: "Evidence on this point is limited/conflicting."\n'
                    'If search results are empty or contain no useful content, output exactly: "No results found for this query."\n\n'
                    "Output plain text only: no bullet points and no markdown."
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
                    "Check whether the findings fully answer the task.\n\n"
                    "Output contract:\n"
                    "- Return ONLY valid JSON with no markdown, no code fences, and no prose.\n"
                    '- Exact schema: {"status":"fully_addressed"|"partially_addressed"|"not_addressed","gap":"..."}\n\n'
                    "Rules:\n"
                    '- Use "fully_addressed" only when the core legal question is answered with specific, source-backed support.\n'
                    '- Otherwise use "partially_addressed" or "not_addressed" and name the single most important gap in "gap" (max 20 words).\n'
                    '- Set "gap" to "" when status is "fully_addressed".\n'
                    "- Entire output must not exceed 40 words including JSON structure."
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
                    "Write a structured legal research report in Markdown using ONLY the provided research notes.\n\n"
                    "The very first characters of your output must be: ## Executive Summary\n"
                    "Do not write any preamble, introduction, or title before the first heading.\n\n"
                    "Required sections in this exact order:\n"
                    "## Executive Summary\n"
                    "## Key Findings\n"
                    "## Legal Implications\n"
                    "## Limitations\n"
                    "## Conclusion\n"
                    "## Sources\n\n"
                    "Rules:\n"
                    "- Do not introduce any legal authority, article, or case not present in the research notes.\n"
                    '- When stating legal points, cite exactly as written in notes (for example: "Under GDPR Article 25..." or "BDSG §26 provides...").\n'
                    "- In Key Findings, group by topic using ### subheadings.\n"
                    '- If support is uncertain or secondary, label it: "(secondary source - verify against primary legislation)".\n'
                    "- In Sources, list every URL from the 'Source URLs' section below, one per line. Include all links; do not omit any.\n"
                    '- In Limitations, include exactly: "This report is for research purposes only and does not constitute legal advice."'
                ),
            },
            {
                "role": "user",
                "content": (
                    "Research Goal: {{goal}}\n\n"
                    "Task Summaries:\n{{task_summaries}}\n\n"
                    "Detailed Research Notes:\n{{context_notes}}\n\n"
                    "Source URLs (include every link in the report Sources section):\n{{source_urls}}"
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
