# Sprint 9 — MLOps I: onboarding-document pipeline (Days 65–72)

**Scenario you build:** Document Intelligence extracts fields from onboarding forms, low-confidence fields go to human review, and a risk-classification model is trained, tracked in MLflow and deployed on Azure ML, with CI/CD for the model.

MLOps comes last on purpose: you already have the platform, pipelines and observability it runs on.

[← Back to tracker](../TRACKER.md)

---

<a id="day-65"></a>
### Day 65 · MLOps · ML fundamentals with scikit-learn

**Time:** ~3 h

**Why it matters:** MLOps interviews still check that you understand what you're operating: metrics, leakage, overfitting.

**Learn**
- **Learning types:** supervised vs unsupervised; classification vs regression.
- **Splits:** train / validation / test, cross-validation, time-based splits.
- **Fit:** overfitting vs underfitting, regularisation.
- **Metrics:** confusion matrix, precision, recall, F1, ROC-AUC, threshold choice by business cost; class imbalance.
- **scikit-learn:** `Pipeline` and `ColumnTransformer` (preprocessing inside the pipeline), data leakage.

**Do**
- [ ] Generate a synthetic mandate-risk dataset (~10k rows, ~5% positive)
- [ ] Pipeline: preprocessing + logistic regression, and + gradient boosting
- [ ] Compare metrics, then pick a decision threshold from an assumed cost of false positives vs false negatives

**Interview questions**
1. **Precision or recall for fraud/risk detection?** — It depends on cost. Missing fraud (low recall) is usually costlier, but too many false alarms (low precision) overload reviewers. Pick the threshold from business cost.
2. **How do you handle imbalanced data?** — Use the right metrics (PR-AUC, recall at fixed precision), class weights, resampling, threshold tuning. Never rely on accuracy.
3. **Give an example of data leakage.** — Scaling or imputing on the full dataset before the split, or a feature that's only known after the outcome (such as "account closed date").

**Gotchas**
- 95% accuracy on 5%-positive data can mean the model predicts "no" for everything.
- Fitting preprocessing outside the pipeline leaks test data.
- Random splits on time-series data.

**Scenario:** the model scores 0.98 AUC in testing and is useless in production. Find the likely leakage.

**Done when:** you can explain your threshold choice in business terms.

**Resources:** [scikit-learn tutorials](https://scikit-learn.org/stable/tutorial/) · [Google ML crash course](https://developers.google.com/machine-learning/crash-course)

---

<a id="day-66"></a>
### Day 66 · MLOps · Experiment tracking and model registry with MLflow

**Time:** ~3 h

**Why it matters:** MLflow is the most widely used open MLOps tool, and Azure ML and Databricks are built around it.

**Learn**
- **Tracking:** parameters, metrics, artifacts, autologging, comparing runs.
- **Models:** flavours, signatures and input examples.
- **Registry:** versions and **aliases** (e.g. `@champion`); stages are deprecated in favour of aliases.
- **Server setup:** backend store (Postgres) + artifact store (blob/S3).
- **LLM features:** MLflow tracing and evaluation for GenAI (awareness).

**Do**
- [ ] Run an MLflow server in Docker with Postgres and blob/MinIO
- [ ] Log both models from Day 65; register the best; set alias `champion`
- [ ] Load the model by alias (`models:/risk@champion`) in a small scoring script

**Interview questions**
1. **How do you reproduce a prediction from six months ago?** — Model version → run ID → code commit, data version/snapshot, environment and parameters, all recorded at training time.
2. **How do models get promoted?** — Register a candidate, evaluate it against the champion on a fixed test set plus business checks, get approval, move the alias, and deploy from the alias.
3. **Why use experiment tracking at all?** — Comparability, reproducibility, collaboration, and an audit trail of which model was trained how.

**Gotchas**
- Artifacts stored on a local disk disappear with the container.
- No signature leads to schema mismatches at serving time.
- Using deprecated stages in new code.

**Scenario:** two data scientists each claim their model is better. How does your setup settle it?

**Done when:** the scoring script loads `@champion` without knowing the version number.

**Resources:** [MLflow docs](https://mlflow.org/docs/latest/) · [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp)

---

<a id="day-67"></a>
### Day 67 · MLOps · Azure Machine Learning: jobs, pipelines, managed endpoints

**Time:** ~3 h

**Why it matters:** Azure-first enterprises run MLOps on Azure ML, and managed endpoints are the common serving choice.

**Learn**
- **Workspace building blocks:** compute clusters, datastores, data assets, environments, MLflow-compatible registry.
- **Jobs and pipelines** with CLI/SDK v2.
- **Managed online endpoints:** deployments, blue/green traffic split, autoscale. Batch endpoints for offline scoring.
- **Security:** managed VNet / private workspace, managed identity.
- **Cost:** clusters with min nodes = 0, quotas.

**Do**
- [ ] Training job on a compute cluster (min nodes 0); register the model
- [ ] Managed online endpoint with two deployments and a 90/10 traffic split
- [ ] Note what this cost vs self-hosting on AKS

**Interview questions**
1. **Managed online endpoints or self-hosting on AKS?** — Managed: less ops, built-in blue/green, monitoring, scaling. AKS: more control, shared platform, potentially cheaper at scale, custom runtimes.
2. **How do you do blue/green for models?** — Two deployments behind one endpoint, shift traffic gradually while comparing metrics, keep instant rollback, use mirrored (shadow) traffic for risk-free tests.
3. **How do you secure an Azure ML workspace?** — Private endpoints/managed VNet, managed identities, RBAC, no public compute IPs, Key Vault for secrets, data access through identity.

**Gotchas**
- A compute cluster with min nodes > 0 bills around the clock.
- Environment (image) builds can take a long time on first use.
- Endpoint and VM quotas per region block deployments.

**Scenario:** the new model version increases approvals by 8% in the canary. Is that good or bad? How do you decide?

**Done when:** traffic is split between two model versions on one endpoint.

**Resources:** [Azure Machine Learning docs](https://learn.microsoft.com/azure/machine-learning/) · [Managed online endpoints](https://learn.microsoft.com/azure/machine-learning/concept-endpoints-online)

---

<a id="day-68"></a>
### Day 68 · AI · Document Intelligence and human review

**Time:** ~3 h

**Why it matters:** document processing (onboarding, invoices, KYC) is one of the most common enterprise AI use cases.

**Learn**
- **Prebuilt models:** read, layout, invoice, ID document, general documents.
- **Custom models:** template vs neural extraction, composed models, training data needs.
- **Confidence scores** and human-in-the-loop review queues.
- **LLM-based extraction:** vision-capable models; trade-offs in accuracy, cost and auditability.

**Do**
- [ ] Extract fields from 10 synthetic onboarding forms with the layout or a custom model
- [ ] Route fields below the confidence threshold to a review queue (Service Bus + a simple review UI or API)
- [ ] Compare against LLM vision extraction on the same 10 docs (accuracy, cost, latency)

**Interview questions**
1. **OCR/extraction service or LLM-based extraction?** — Use a specialised service for high-volume, standard forms with confidence scores and lower cost. Use LLMs for messy, variable documents and reasoning. Often combine them: layout first, LLM second.
2. **How do you handle low-confidence results?** — Per-field thresholds, human review queues, feedback into retraining, and tracking accuracy over time.
3. **How do you scale to 100,000 documents a day?** — Async batch processing via queues, parallel workers, rate-limit awareness, retries, idempotent processing, and cost monitoring.

**Gotchas**
- Scanned, rotated or low-resolution documents reduce accuracy a lot.
- Long-running async operations need polling and timeouts.
- PII left in intermediate blobs and logs.

**Scenario:** a regulator wants to know why a customer's application was flagged. Trace it back through the document pipeline.

**Done when:** every extracted field has a confidence score and an audit trail.

**Resources:** [Document Intelligence docs](https://learn.microsoft.com/azure/ai-services/document-intelligence/) · [Azure AI Search + Document Intelligence](https://learn.microsoft.com/azure/search/cognitive-search-skill-document-intelligence-layout)

---

<a id="day-69"></a>
### Day 69 · AI · Multi-agent patterns, and fine-tuning vs RAG vs prompting

**Time:** ~3 h

**Why it matters:** interviewers test judgement here: knowing when *not* to use multi-agent systems or fine-tuning.

**Learn**
- **Multi-agent patterns:** supervisor/orchestrator, sequential pipeline, handoff, group chat. Cost and complexity grow fast.
- **The decision:** prompting (instructions, examples) → RAG (knowledge) → fine-tuning (format, style, narrow skills, smaller/faster models).
- **Fine-tuning basics:** supervised fine-tuning, LoRA, distillation (awareness), hosting cost and model retirement.

**Do**
- [ ] Build the onboarding flow as a supervisor + 3 agents (extractor → checker → approver)
- [ ] Compare with a single-agent version on 10 cases: quality, tokens, latency
- [ ] Write `docs/adr/008-fine-tune-vs-rag.md` for this use case

**Interview questions**
1. **When would you fine-tune instead of using RAG?** — Fine-tune for consistent format, style or a narrow task, or to shrink a model. Use RAG for knowledge that changes or must be cited. Fine-tuning is a poor way to add facts.
2. **When is a multi-agent system worth it?** — When sub-tasks need different tools, prompts or permissions and can be evaluated separately. Otherwise one agent or a workflow is cheaper and more reliable.
3. **How do you evaluate a multi-agent system?** — Per-agent evaluations, end-to-end task success, trajectory checks, and cost/latency per task.

**Gotchas**
- Agents talking to each other multiply token usage.
- Fine-tuning to "teach the model our documents".
- Fine-tuned models need re-tuning when the base model is retired.

**Scenario:** a vendor pitches a 7-agent system for invoice processing. Evaluate the pitch.

**Done when:** your ADR states a clear recommendation backed by your 10-case comparison.

**Resources:** [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · [LangGraph multi-agent docs](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)

---

<a id="day-70"></a>
### Day 70 · DevOps · CI/CD for machine learning

**Time:** ~3 h

**Why it matters:** "how do models get to production safely?" is the central MLOps interview question.

**Learn**
- **Pipeline stages:** data validation → train → evaluate → compare to champion → register → approve → deploy.
- **Triggers:** code change, new data, schedule, drift alert.
- **Quality gates:** metric thresholds, fairness/sanity checks, schema checks.
- **Tooling:** GitHub Actions or Azure DevOps driving Azure ML jobs (CLI v2).

**Do**
- [ ] Workflow: on push to `main`, run training in Azure ML, compare to `@champion`, register if better
- [ ] Require manual approval before the endpoint deployment
- [ ] Data validation step (schema + basic stats) that fails the run on bad data

**Interview questions**
1. **What should trigger retraining?** — A schedule for slowly changing data, drift or performance alerts, new labelled data volume, or a code change. Always gated by evaluation.
2. **How do you gate a model release?** — Beats the champion on the holdout set, passes sanity and fairness checks, latency within budget, human approval for high-risk models.
3. **What does "CI for data" mean?** — Schema, range, null and distribution checks on incoming data before training or scoring.

**Gotchas**
- Non-deterministic training makes champion comparisons noisy. Fix seeds and compare on fixed sets.
- Training data not versioned, so results can't be reproduced.
- Deploying straight to 100% traffic.

**Scenario:** a retrained model passed all metrics but customer complaints doubled. What did the pipeline miss?

**Done when:** a worse model is automatically rejected by the pipeline.

**Resources:** [MLOps with Azure ML](https://learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment) · [Google: MLOps levels](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

---

<a id="day-71"></a>
### Day 71 · .NET + Design · Data architecture choices

**Time:** ~2 h

**Why it matters:** architects are expected to choose the right store per use case and explain the trade-offs.

**Learn**
- **OLTP vs OLAP;** relational vs document vs key-value vs graph vs vector stores.
- **CAP / PACELC** in practice.
- **Change data capture** for integrating operational and analytical systems.
- **Lakehouse awareness:** Microsoft Fabric / Databricks.
- **Polyglot persistence:** benefits vs operational cost.

**Do**
- [ ] 45-minute drill: data architecture for banking onboarding (operational DB, document store, search, vector, analytics, audit) in `design/data-architecture.md`

**Interview questions**
1. **Which database for mandates, chat history, documents, search and analytics?** — SQL; Cosmos DB/document store; Blob; AI Search (+ vectors); lakehouse/warehouse via CDC. Justify each by access pattern.
2. **When do you use change data capture?** — To feed search indexes, analytics or other services from the system of record without dual writes.
3. **A separate vector DB, or pgvector in your existing Postgres?** — pgvector when scale is moderate and you value one system. A dedicated store/AI Search when you need hybrid search, scale or managed features.

**Gotchas**
- Too many databases for a small team to operate.
- Dual writes instead of CDC/outbox.
- Running analytics queries on the OLTP database.

**Scenario:** reporting queries are slowing down customer transactions. Fix it without a big rewrite.

**Done when:** every store in your diagram has one sentence of justification.

**Resources:** [Choose a data store](https://learn.microsoft.com/azure/architecture/guide/technology-choices/data-store-overview) · [Designing Data-Intensive Applications (book)](https://dataintensive.net/)

---

<a id="day-72"></a>
### Day 72 · Build + Defend · Onboarding-document pipeline

**Time:** ~4 h

**Do**
- [ ] Upload a form → extraction → human review for low-confidence fields → risk model score → approval agent
- [ ] Model trained via the pipeline, tracked in MLflow, deployed with blue/green
- [ ] README section: the model card (data, metrics, threshold, limitations)
- [ ] Record answers to the three questions below

**Interview questions**
1. **A model works in the notebook and fails in production. List the likely causes.** — Training/serving skew (different preprocessing), data drift, missing features at inference, environment or library differences, leakage in training, wrong threshold.
2. **How do you version data, code and model together so a prediction can be reproduced?** — Your MLflow run, git SHA, data snapshot and environment, shown live.
3. **When would you fine-tune instead of using RAG?** — Your ADR-008.

**Gotchas**
- The review queue becomes a bottleneck. Track its backlog as a metric.

**Done when:** one document can be traced from upload to final decision, with every model and human step visible.
