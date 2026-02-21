"""
Create a Langfuse evaluation dataset for LexAgent.
Run once: uv run python scripts/create_eval_dataset.py

Dataset contains golden examples for each prompt type.
Use Langfuse dashboard to add more examples over time.
"""

from dotenv import load_dotenv
from langfuse import get_client

load_dotenv()
langfuse = get_client()

DATASET_NAME = "lexagent-eval-v1"

# Golden examples: (input_variables, expected_output_characteristics)
EXAMPLES = [
    {
        "name": "reflect-fully-addressed",
        "input": {
            "task_description": "Find GDPR Article 5 data minimisation requirements",
            "findings": "GDPR Article 5(1)(c) requires personal data to be adequate, relevant and limited to what is necessary. (EUR-Lex, https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679)",
        },
        "expected_output": '{"status":"fully_addressed","gap":""}',
        "metadata": {"prompt": "legal-research/reflect", "type": "positive"},
    },
    {
        "name": "reflect-partially-addressed",
        "input": {
            "task_description": "Find GDPR Article 5 data minimisation requirements including enforcement examples",
            "findings": "GDPR Article 5(1)(c) requires data minimisation. No enforcement cases found.",
        },
        "expected_output": '{"status":"partially_addressed","gap":"No enforcement examples found for data minimisation violations"}',
        "metadata": {"prompt": "legal-research/reflect", "type": "negative"},
    },
    {
        "name": "reflect-no-results",
        "input": {
            "task_description": "Find applicable German privacy law for employee monitoring",
            "findings": "No results found for this query.",
        },
        "expected_output": '{"status":"not_addressed","gap":"No sources found for German employee monitoring privacy law"}',
        "metadata": {"prompt": "legal-research/reflect", "type": "negative"},
    },
    {
        "name": "plan-gdpr-basic",
        "input": {"goal": "Research GDPR compliance requirements for a German SaaS startup collecting user data"},
        "expected_output": "3-6 tasks, first task identifies jurisdiction if ambiguous, no compile/synthesize task",
        "metadata": {"prompt": "legal-research/generate-plan", "type": "plan"},
    },
]


def create_dataset():
    print(f"\nCreating dataset: {DATASET_NAME}")
    try:
        dataset = langfuse.create_dataset(
            name=DATASET_NAME,
            description="Golden examples for LexAgent prompt evaluation",
        )
        print(f"✅ Dataset created: {dataset.name}")
    except Exception as e:
        print(f"Dataset may already exist: {e}")

    for ex in EXAMPLES:
        langfuse.create_dataset_item(
            dataset_name=DATASET_NAME,
            input=ex["input"],
            expected_output=ex["expected_output"],
            metadata=ex.get("metadata", {}),
        )
        print(f"  ✅ Added item: {ex['name']}")

    print(f"\n✅ Dataset '{DATASET_NAME}' ready in Langfuse dashboard.")
    print("Add more examples via the Langfuse UI over time.")


if __name__ == "__main__":
    create_dataset()
