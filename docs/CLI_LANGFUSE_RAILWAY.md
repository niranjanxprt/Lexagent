# Langfuse and Railway via CLI

You can update Langfuse prompts and configure Railway (volumes, variables) from the command line instead of the web dashboards.

---

## Langfuse CLI

### Prerequisites

- Node.js (for `npx`)
- `.env` in the repo root with:
  - `LANGFUSE_PUBLIC_KEY=pk-lf-...`
  - `LANGFUSE_SECRET_KEY=sk-lf-...`
  - Optionally `LANGFUSE_HOST=https://cloud.langfuse.com`

### One-shot: update all prompts (V4)

From the repo root:

```bash
bash scripts/update_langfuse_prompts_cli.sh
```

This runs `app/init_langfuse_prompts.py`, which creates a **new version** of each of the 5 prompts with the current V4 text and the **production** label. No dashboard step needed. Prompt content is defined in `app/init_langfuse_prompts.py`; see [LEGAL_RESEARCH_PROMPTS_V4.md](LEGAL_RESEARCH_PROMPTS_V4.md) for a single-file copy.

### Other useful commands

```bash
# List prompts and versions
npx langfuse-cli --env .env api prompts list

# Get a specific prompt
npx langfuse-cli --env .env api prompts get "legal-research/generate-plan" --json
```

To change prompt text: edit `app/init_langfuse_prompts.py` and re-run the script, or edit directly in the Langfuse UI (UI changes take effect without redeploy; see [LANGFUSE_SETUP.md](LANGFUSE_SETUP.md)).

---

## Railway CLI

### Prerequisites

- [Railway CLI](https://docs.railway.com/guides/cli) installed (`npm i -g @railway/cli` or `brew install railway`)
- Logged in: `railway login`
- Project linked: `railway link` (or run from a directory already linked)

### One-shot: volume for session persistence

From the repo root:

```bash
bash scripts/railway_setup_volume_and_vars.sh
```

This runs `railway volume add --mount-path /app/data` so sessions persist across redeploys.

### Manual commands

```bash
# Add volume for session data (required for persistence)
railway volume add --mount-path /app/data

# Optional: volume for report files
railway volume add --mount-path /app/reports

# Optional: use gpt-4o for legal reasoning
railway variables --set OPENAI_MODEL=gpt-4.1-mini

# List volumes and variables
railway volume list
railway variables
```

### Service and environment

If you have multiple services or environments:

```bash
railway service          # link which service to use
railway environment      # switch environment
railway volume add -m /app/data -s <SERVICE_ID>
```

---

## Quick reference

| Goal | Command |
|------|---------|
| Update all Langfuse prompts (Block D) | `bash scripts/update_langfuse_prompts_cli.sh` |
| Add Railway volume `/app/data` | `railway volume add --mount-path /app/data` |
| Set Railway model | `railway variables --set OPENAI_MODEL=gpt-4.1-mini` |
| List Langfuse prompts | `npx langfuse-cli --env .env api prompts list` |
| List Railway volumes | `railway volume list` |
