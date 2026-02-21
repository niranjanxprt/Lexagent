# Evaluation Design

## Philosophy

Legal research quality is hard to measure with simple accuracy metrics — the same question can have multiple valid answers depending on jurisdiction, recency, and depth. This evaluation combines structured criteria (what must be present) with optional LLM-as-judge scoring (is the reasoning sound).

## Per-Scenario Evaluation

### Scenario 1: GDPR AI Compliance

**Goal prompt:** "What are the key GDPR requirements for deploying AI systems in Germany?"

**Required elements (checklist):**
- [ ] GDPR Article 5 (lawfulness, fairness, transparency; data minimisation)
- [ ] GDPR Article 25 (data protection by design and by default)
- [ ] GDPR Article 32 (security of processing)
- [ ] At least one BDSG reference (German national implementation)
- [ ] Minimum 3 source URLs from official/authoritative sources
- [ ] No hallucinated article numbers (cross-check each citation)

**Pass:** All 6 items met. **Partial:** 4–5 items. **Fail:** &lt;4 items or hallucinated citations.

---

### Scenario 2: EU AI Act — High-Risk Systems

**Goal prompt:** "What obligations apply to high-risk AI systems under the EU AI Act?"

**Required elements:**
- [ ] Article 9 (risk management system)
- [ ] Article 13 (transparency and provision of information)
- [ ] Article 16 (obligations of providers of high-risk AI systems)
- [ ] Clear distinction between provider and deployer obligations
- [ ] Reference to Annex III or official EU publication
- [ ] At least one EUR-Lex or official EU URL

**Pass:** 5–6 items. **Partial:** 3–4. **Fail:** &lt;3.

---

### Scenario 3: BRAO — AI in Legal Practice

**Goal prompt:** "Can law firms in Germany use AI tools to draft client documents under BRAO?"

**Required elements:**
- [ ] §43a BRAO (general professional duties)
- [ ] §2 BRAO (definition of legal service)
- [ ] Verschwiegenheitspflicht (professional confidentiality)
- [ ] Discussion of liability for AI-generated errors
- [ ] Distinction between AI-assisted drafting vs. AI replacing lawyer judgment

**Pass:** 4–5 items. **Partial:** 2–3. **Fail:** &lt;2.

---

### Scenario 4: Employee Monitoring (BDSG)

**Goal prompt:** "What data protection rules apply to employee monitoring software in Germany?"

**Required elements:**
- [ ] §26 BDSG (processing employee data)
- [ ] Betriebsrat (works council) co-determination rights
- [ ] Proportionality principle (Verhältnismäßigkeit)
- [ ] Distinction between monitoring of time/location vs. content/communication
- [ ] Reference to relevant BAG case law where applicable

**Pass:** 4–5 items. **Partial:** 2–3. **Fail:** &lt;2.

---

### Scenario 5: AI-Generated Contracts

**Goal prompt:** "What are the legal risks of using AI-generated contracts in German commercial law?"

**Required elements:**
- [ ] BGB §305 (standard business terms — AGB)
- [ ] BGB §§133, 157 (interpretation principles)
- [ ] Current absence of specific AI-contract legislation
- [ ] Signature and authentication issues
- [ ] Recommended mitigation: human legal review

**Pass:** 4–5 items. **Partial:** 2–3. **Fail:** &lt;2.

---

## How to Run Evaluations

**Manual (current):**
1. Run the demo goal through the system (React).
2. Open the generated markdown report.
3. Check each required element against the checklist.
4. Score Pass / Partial / Fail.

**LLM-as-judge (optional):** After each session, prompt GPT-4 to rate the report 1–5 on: factual accuracy, legal specificity, source attribution, completeness. Store scores in Langfuse linked to the prompt version for regression tracking.

**Regression:** Keep gold-standard reports for each scenario; when prompt versions change, re-run and verify success criteria are still met.

**Hallucination detection:** Cross-reference article numbers in the final report against source URLs in the research notes; citations not traceable to a source are hallucination flags.

---

## Simple Eval (no server, no traces)

The easiest way to run evals is a **local script** that uses a small JSON dataset and the agent in-process. No Langfuse traces or running server needed.

### Sample dataset

**`scripts/eval_dataset.json`** — 3 goals with optional `expected_keywords` for a simple pass/fail check:

- **gdpr-ai** — GDPR requirements for AI in Germany (check: GDPR, Article, BDSG)
- **eu-ai-act** — High-risk AI obligations under EU AI Act (check: AI Act, high-risk, Article)
- **employee-monitoring** — Data protection for employee monitoring in Germany (check: BDSG, data protection, employee)

You can edit this file: add more items, change goals, or add/remove `expected_keywords` (if missing, the script only runs and saves the report).

### Run

From repo root. Ensure `.env` has valid `OPENAI_API_KEY` and `TAVILY_API_KEY` (Langfuse is optional; the script will use fallback prompts if unset).

```bash
# Run all 3 items
uv run python scripts/run_simple_eval.py

# Quick test: run only the first item
uv run python scripts/run_simple_eval.py --limit 1

# Run all but skip keyword check (only generate and save reports)
uv run python scripts/run_simple_eval.py --no-check
```

The script runs plan → execute all tasks → report for each goal, writes reports to `reports/` (e.g. `eval-gdpr-ai-<uuid>.md`), and prints Pass/Fail per item and a short summary. Exit code 0 only if all pass.

---

## Reflect eval scripts (Langfuse dataset)

The repo includes scripts that create and run a **reflect**-focused eval against a Langfuse dataset (no full agent run; just the reflect prompt and scoring).

**Data:** You have **golden data** once the dataset is created: run `uv run python scripts/create_eval_dataset.py` to populate `lexagent-eval-v1` with 4 items (3 reflect + 1 plan). For more coverage, add items from production traces (see [Build a dataset from traces](#1-build-a-dataset-from-traces-ui) below).

**Scoring options:**

| Method | Script | Use when |
|--------|--------|----------|
| **Deterministic** | `run_eval.py` | You want exact status match (fast, no extra LLM cost). |
| **LLM-as-a-Judge** | `run_eval_llm_judge.py` | You want semantic correctness (status + gap) or qualitative scoring. |

- **Dataset name:** `lexagent-eval-v1`
- **Create dataset (one-time):** `scripts/create_eval_dataset.py` — creates the dataset with golden examples (reflect + one plan example). Run: `uv run python scripts/create_eval_dataset.py`
- **Run reflect eval (deterministic):** `scripts/run_eval.py` — loads the dataset, filters items for `legal-research/reflect`, runs each through the reflect prompt, scores JSON output (status match), and posts scores to Langfuse via `item.run(...)` and `root_span.score_trace(...)`. Run: `uv run python scripts/run_eval.py`
- **Run reflect eval (LLM-as-a-Judge):** `scripts/run_eval_llm_judge.py` — same dataset and reflect prompt, but one or more judge models (default: GPT-4.1 and GPT-4.1-mini) score 0–1 whether the output is semantically correct (status and gap). Run: `uv run python scripts/run_eval_llm_judge.py` or use the CLI wrapper below.

Requires `.env` with Langfuse and OpenAI keys. Scores appear in the Langfuse dashboard under the dataset run.

### LLM-as-a-Judge with GPT-4.1 and GPT-4.1-mini (Langfuse CLI)

To run both judges and register score configs via the Langfuse CLI:

1. **One-time: create score configs** (so scores show in the dashboard with the right names and 0–1 range):

   ```bash
   npx langfuse-cli --env .env api score-configs create --name "reflect-llm-judge-gpt-4.1" --dataType NUMERIC --minValue 0 --maxValue 1 --description "LLM-as-judge (GPT-4.1) for reflect step"
   npx langfuse-cli --env .env api score-configs create --name "reflect-llm-judge-gpt-4.1-mini" --dataType NUMERIC --minValue 0 --maxValue 1 --description "LLM-as-judge (GPT-4.1-mini) for reflect step"
   ```

2. **Run the eval** (both judges on the 4 dataset items; scores are posted to Langfuse):

   ```bash
   ./scripts/run_eval_llm_judge_cli.sh
   ```

   The script uses the Langfuse CLI for score configs and dataset listing, Python for the eval, and the SDK for posting scores. To post scores via **curl** (Langfuse REST API) instead of the SDK—e.g. when the CLI `scores create` lacks `--value`—use:

   ```bash
   ./scripts/run_eval_llm_judge_cli.sh --scores-via-curl
   ```

   That flow writes trace IDs and scores to a temp file, then `post_scores_via_curl.sh` posts each via `curl` to `POST /api/public/scores`. To use only one judge: `uv run python scripts/run_eval_llm_judge.py --judges gpt-4.1`.

3. **Optional CLI checks:**

   ```bash
   npx langfuse-cli --env .env api score-configs get-public
   npx langfuse-cli --env .env api datasets get-get-runs lexagent-eval-v1 --limit 5
   npx langfuse-cli --env .env api score-v2s get-scores --limit 10
   ```

   **Note:** The Langfuse CLI `scores create` does not expose a `--value` parameter. To create scores from the command line, use `./scripts/run_eval_llm_judge_cli.sh --scores-via-curl`, which posts scores via the REST API with `curl`.

### Where scores appear in Langfuse (script-based eval)

Our scripts (`run_eval.py`, `run_eval_llm_judge.py`) post scores via `root_span.score_trace(name=..., value=...)` inside `item.run()`. You **do not** see an "Evaluator" in the Langfuse UI because we use a custom script, not Langfuse's managed evaluator. Scores appear here:

1. **Datasets** → **lexagent-eval-v1** → **Runs** tab
2. Click a run (e.g. `reflect-eval-llm-judge-v1`)
3. Each run item has a trace; open it to see scores (`reflect-llm-judge-gpt-4.1`, `reflect-llm-judge-gpt-4.1-mini`, etc.)
4. **Analytics** → **Scores** → filter by object type **Dataset Run Items** to compare across runs

Score configs (created via CLI) define the schema (name, 0–1 range) so scores display correctly in the dashboard.

### Creating a Langfuse Evaluator (UI-based, for Prompt Experiments)

To have Langfuse **automatically** score outputs when you run experiments from the UI (Datasets → Start Experiment):

1. **Evaluators** → **Set up Evaluator**
2. **Default model:** Choose an LLM connection (e.g. GPT-4.1-mini) for the judge
3. **Evaluator:** Pick **Custom Evaluator** (or a Managed one like Correctness)
4. **Evaluation prompt:** Use placeholders `{{input}}`, `{{output}}`, `{{ground_truth}}` and a rubric (e.g. "Score 0–1: 1 = output matches expected status and gap")
5. **Target:** **Offline Experiment Data** → filter by dataset `lexagent-eval-v1`
6. **Variable mapping:** Map `input` → dataset item `input`, `output` → trace output, `ground_truth` → `expected_output`
7. Save. When you run a Prompt Experiment (Datasets → Start Experiment → Create), select this evaluator; it will run automatically and attach scores.

See [Langfuse: LLM-as-a-Judge](https://langfuse.com/docs/evaluation/evaluation-methods/llm-as-a-judge) for the full UI flow.

### LLM-as-a-Judge (reflect and beyond)

[LLM-as-a-Judge](https://langfuse.com/docs/evaluation/llm-as-a-judge) is an evaluation method where a judge model assesses application outputs against a rubric (input, output, optional ground truth). It scales better than human review and captures nuance when the rubric is clear.

- **In this repo:** `scripts/run_eval_llm_judge.py` implements a custom judge for the reflect step (rubric: correct status and gap). You can extend the same pattern for report quality (e.g. accuracy, specificity, citations) and post scores via `root_span.score_trace(...)`.
- **In Langfuse:** For Experiments (dataset runs), you can attach **Managed** or **Custom** evaluators in the UI so the judge runs automatically on each run. Evaluators → Set up Evaluator → choose target **Offline Experiment Data** → map variables (e.g. `input`, `output`, `ground_truth`) to your dataset item fields. See [Langfuse: LLM-as-a-Judge](https://langfuse.com/docs/evaluation/llm-as-a-judge) for the full setup (default model, rubric, variable mapping, Experiments via UI/SDK).

**Is the dataset already in Langfuse?** No. The dataset `lexagent-eval-v1` is created when you run the create script (or the CLI/UI steps below). Until then, it does not exist in your Langfuse project.

**Create the dataset via Langfuse CLI (optional):** You can create the empty dataset with the CLI, then add items via the Python script or UI:

```bash
# Create empty dataset
npx langfuse-cli --env .env api datasets create --name lexagent-eval-v1 --description "Golden examples for LexAgent prompt evaluation"

# List datasets to confirm
npx langfuse-cli --env .env api datasets list

# List items in the dataset (use --dataset-name)
npx langfuse-cli --env .env api dataset-items list --dataset-name lexagent-eval-v1
```

To add the golden items (input, expected_output, metadata), the Python script is the easiest: run `uv run python scripts/create_eval_dataset.py`. The script will create the dataset if it does not exist, then add all items. Alternatively add items in the Langfuse UI (Datasets → lexagent-eval-v1 → Add item) or via the API/CLI with JSON body for each item.

---

## Eval Using Langfuse Logs (Traces)

You can turn production or test traces into datasets, run experiments (e.g. different prompt versions), and attach scores so evals are repeatable and comparable.

### 1. Build a dataset from traces (UI)

1. In Langfuse, go to **Traces** (or **Observations**).
2. Open a trace from a session you care about (e.g. a full run that produced a report).
3. Select one or more **observations** (e.g. the `generate-report` generation, or the whole trace).
4. Click **Actions** → **Add to dataset**.
5. Choose **Create new dataset** or an existing one (e.g. `legal-research-eval`).
6. **Map fields:** e.g. map the observation **input** to the dataset item **input** (e.g. `goal`, `task_summaries`, `context_notes`, `source_urls` for report eval), and optionally map **output** to **expected output** (or leave expected output blank and score later).
7. Confirm. The trace is linked to the dataset item via `sourceTraceId` / `sourceObservationId`.

Repeat for more traces (good and bad) so the dataset represents the cases you want to regress on.

### 2. Build a dataset from traces (SDK)

```python
from langfuse import get_client
langfuse = get_client()

# Create dataset
langfuse.create_dataset(name="legal-research-eval", description="Sessions from traces for report eval")

# Add item from a trace you already have (e.g. trace_id from Langfuse UI or API)
langfuse.create_dataset_item(
    dataset_name="legal-research-eval",
    input={"goal": "What are the key GDPR requirements for AI in Germany?"},  # or full input from trace
    expected_output={"pass": true, "notes": "GDPR 5, 25, 32; BDSG; 3+ URLs"},  # optional
    source_trace_id="<trace_id>",
    source_observation_id="<observation_id>",  # optional
)
```

Use **input** keys that match your prompt variables (e.g. `goal` for generate-plan; `goal`, `task_summaries`, `context_notes`, `source_urls` for generate-report) if you will run prompt experiments against this dataset.

### 3. List traces / get trace (CLI)

```bash
# List recent traces (e.g. to copy trace IDs for dataset items or scoring)
npx langfuse-cli --env .env api traces list --limit 20

# Get one trace (full input/output and observation IDs)
npx langfuse-cli --env .env api traces get <trace_id>
```

Use these to inspect runs and to pass `trace_id` into the SDK or into a script that creates dataset items or scores.

### 4. Run an experiment (UI — Prompt Experiment)

1. Go to **Datasets** → select your dataset (e.g. `legal-research-eval`).
2. Click **Start Experiment** → **Create** (Prompt Experiment).
3. Select **prompt** (e.g. `legal-research/generate-report`) and **prompt version** (e.g. production).
4. Select **dataset** and **LLM connection** (model).
5. Optionally add an **LLM-as-a-Judge** evaluator (target: Experiment runs, filter by this dataset) to score outputs vs expected output.
6. Run. Langfuse executes the prompt for each dataset item and records a **dataset run**. You can compare runs (e.g. old vs new prompt version).

For LexAgent, single-step experiments (e.g. only generate-report) need dataset items whose **input** has keys matching that prompt’s variables: `goal`, `task_summaries`, `context_notes`, `source_urls`. You can build those from the `generate-report` observation’s input in traces.

### 5. Run an experiment (SDK)

```python
from langfuse import get_client
langfuse = get_client()

dataset = langfuse.get_dataset("legal-research-eval")

def run_report(item):
    # Your app logic: call LLM with prompt + item.input, return output
    # Or use Langfuse prompt + item.input for generate-report
    ...

result = dataset.run_experiment(name="v4-report-eval", task=run_report)
# Inspect result, scores, and the run in Langfuse UI under Dataset Runs
```

### 6. Add scores to traces (manual or API)

- **UI:** Open a **trace** → add a **score** (e.g. name `report_quality`, value 1–5 or pass/fail). Useful for one-off or human eval.
- **CLI:** Create a score for a trace (e.g. after you run an external eval script):
  ```bash
  npx langfuse-cli --env .env api scores create --traceId <trace_id> --name report_quality --value 0.85
  ```
- **SDK:** `langfuse.score(trace_id=..., name="report_quality", value=0.85)` (or session-level score). Use this from your own eval script that reads trace output and computes a metric. For **dataset-based evals**, use `item.run(...)` as a context manager and `root_span.score_trace(name=..., value=...)` so scores attach to the dataset run (see `scripts/run_eval.py`).

Linking scores to traces (and to prompt versions via the trace’s generations) lets you compare prompt versions in Langfuse (e.g. Metrics per prompt version).

### 7. Suggested LexAgent eval flow

1. **Collect:** Run 5–10 sessions (mix of scenarios above); ensure Langfuse is receiving traces.
2. **Dataset:** From Langfuse UI, add the report-generation observations (or full-session traces) to a dataset; map input (e.g. goal, context, source_urls) and optionally expected output (checklist or gold summary).
3. **Baseline:** Run a Prompt Experiment on that dataset with current production prompt; optionally attach an LLM-as-judge evaluator. Record scores.
4. **Regression:** After changing a prompt (in code or in Langfuse UI), re-run the same experiment and compare scores and outputs.
5. **Ongoing:** Add new traces (edge cases, failures) to the dataset; re-run experiments before promoting new prompt versions to production.

---

## What Good Looks Like (Example)

A strong report for Scenario 1 would:
- Open with a 3–4 sentence executive summary naming GDPR, EU AI Act, and BDSG.
- Dedicate a section to each major article (5, 25, 32) with brief quoted legal text.
- Note Germany-specific considerations (BDSG §22 for special categories, relevant DSK guidance).
- Include 4–6 source URLs, at least 2 from eur-lex.europa.eu or gesetze-im-internet.de.
- Close with a Limitations section noting recency (GDPR/AI Act guidance evolves).

The system does not yet achieve this consistently — the reflect step sometimes returns "task adequately answered" for thin results. Improving the reflect prompt is high leverage.
