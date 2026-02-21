# Langfuse Prompt Management Setup for LexAgent

This guide explains how to externalize LexAgent prompts to Langfuse for centralized management and non-technical editing.

## What Changed

All 5 hardcoded prompts in `app/agent.py` have been moved to Langfuse:

1. **legal-research/generate-plan** - Decomposes research goal into tasks
2. **legal-research/refine-query** - Refines search query based on context
3. **legal-research/compress-results** - Compresses search results into summary
4. **legal-research/reflect** - Evaluates task completion
5. **legal-research/generate-report** - Synthesizes final markdown report

## Benefits

✅ **No Code Deployment**: Non-technical users update prompts directly in Langfuse
✅ **Version Control**: All prompt changes tracked with versions and labels
✅ **Low Latency**: Prompts cached client-side (60s TTL by default)
✅ **Easy A/B Testing**: Create multiple prompt versions and switch between them
✅ **Audit Trail**: See who changed what prompt and when

## Setup Instructions

### 1. Verify Langfuse Credentials

Ensure your `.env` file has:
```bash
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com  # or self-hosted URL
```

### 2. Initialize Prompts in Langfuse

Run the initialization script to create all 5 prompts:
```bash
uv run python app/init_langfuse_prompts.py
```

This creates all prompts with the `production` label, making them immediately available to the agent.

### 3. Verify Prompts in Langfuse Dashboard

1. Go to your Langfuse dashboard
2. Navigate to **Prompt Management**
3. You should see 5 prompts under `legal-research/` folder:
   - generate-plan
   - refine-query
   - compress-results
   - reflect
   - generate-report

## How It Works

### Fetching Prompts

When the agent runs, it:
1. Calls `langfuse.get_prompt("legal-research/generate-plan", type="chat")`
2. SDK checks local cache (60s TTL)
3. If cached, returns immediately (no latency)
4. If cache expired, fetches from Langfuse in background
5. Calls `.compile(variables)` to substitute variables into prompt

Example:
```python
prompt = langfuse.get_prompt("legal-research/generate-plan", type="chat")
messages = prompt.compile(goal="Research AI Act compliance")
# -> [
#      {"role": "system", "content": "You are a senior legal research assistant..."},
#      {"role": "user", "content": "Legal research goal: Research AI Act compliance"}
#    ]
```

### Linking Prompts to Traces

When you pass `langfuse_prompt=prompt` to `call_llm()`, Langfuse automatically:
- Links the trace to the specific prompt version
- Records which prompt version was used for each LLM call
- Allows you to compare performance across prompt versions

## Updating Prompts

### In Langfuse UI

1. Go to **Prompt Management**
2. Click on any prompt to edit
3. Modify the system message or user message template
4. Click **Save** to create a new version
5. New versions are automatically labeled with `latest`
6. To deploy to production, add the `production` label to the new version

### Variable Names

All variables use double curly braces: `{{variable_name}}`

Available variables by prompt:

**generate-plan**
- `{{goal}}` - The legal research goal

**refine-query**
- `{{task_title}}` - Task title
- `{{task_description}}` - Task description
- `{{context_notes}}` - Prior research context

**compress-results**
- `{{task_title}}` - Task title
- `{{search_results}}` - Search result snippets

**reflect**
- `{{task_description}}` - Task description
- `{{findings}}` - Compressed findings from search

**generate-report**
- `{{goal}}` - Original research goal
- `{{task_summaries}}` - Bulleted list of task results
- `{{context_notes}}` - All accumulated research notes

## Caching Behavior

The Langfuse SDK caches prompts locally for 60 seconds. This means:

- **First call**: Fetches from Langfuse, caches it
- **Within 60s**: Returns cached version (instant)
- **After 60s**: Returns stale cache while fetching fresh version in background
- **Next call after that**: Returns the fresh version

### Disable Caching (Development Only)

For testing prompt changes immediately:
```python
prompt = langfuse.get_prompt("legal-research/generate-plan", cache_ttl_seconds=0, type="chat")
```

⚠️ This adds a network request on every call - only use for development!

## Fallback Behavior

If Langfuse is unavailable, the agent will fail gracefully (no silent fallback). This is intentional - it helps you catch connectivity issues.

If you want to add a fallback prompt for resilience, you can use:
```python
from langfuse import LangfuseError

try:
    prompt = langfuse.get_prompt("legal-research/generate-plan", type="chat")
except LangfuseError:
    # Use hardcoded fallback
    prompt = PromptClient([...hardcoded messages...])
```

## Monitoring Prompt Usage

In your Langfuse dashboard, you can:

1. **View Traces by Prompt**: See all LLM calls using a specific prompt version
2. **Compare Metrics**: Track completion time, token usage, and cost by prompt version
3. **Version Comparison**: See diffs between prompt versions
4. **Rollback**: Instantly revert to a previous prompt version via `production` label

## Troubleshooting

### Prompts Not Found

```
Error: Prompt "legal-research/generate-plan" not found
```

**Solution**: Run the initialization script again
```bash
uv run python app/init_langfuse_prompts.py
```

### Old Prompts Still Being Used

Prompts are cached for 60 seconds. To force an immediate refresh:
```python
prompt = langfuse.get_prompt("legal-research/generate-plan", cache_ttl_seconds=0, type="chat")
```

### Network Errors

If you see connection errors, verify:
- `LANGFUSE_BASE_URL` is correct
- Network connectivity to Langfuse (cloud or self-hosted)
- API keys are valid

## Next Steps

1. ✅ Run `uv run python app/init_langfuse_prompts.py`
2. ✅ Verify prompts in Langfuse dashboard
3. ✅ Start the agent: `make dev` (backend + React) or `make backend` and `make react` in separate terminals
4. ✅ Create a research session and execute tasks
5. ✅ Watch prompts being used in Langfuse dashboard
6. ✅ Edit prompts and see changes reflected on next task execution (within cache TTL)

## Reverting to Hardcoded Prompts

If you want to revert to hardcoded prompts, see `app/agent.py.backup` (which doesn't exist, but you can revert via git):
```bash
git checkout HEAD -- app/agent.py
```

This will restore the original hardcoded prompts.
