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

## What Good Looks Like (Example)

A strong report for Scenario 1 would:
- Open with a 3–4 sentence executive summary naming GDPR, EU AI Act, and BDSG.
- Dedicate a section to each major article (5, 25, 32) with brief quoted legal text.
- Note Germany-specific considerations (BDSG §22 for special categories, relevant DSK guidance).
- Include 4–6 source URLs, at least 2 from eur-lex.europa.eu or gesetze-im-internet.de.
- Close with a Limitations section noting recency (GDPR/AI Act guidance evolves).

The system does not yet achieve this consistently — the reflect step sometimes returns "task adequately answered" for thin results. Improving the reflect prompt is high leverage.
