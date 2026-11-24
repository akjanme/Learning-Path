# Sprint 10 — MLOps II: model and prompt lifecycle (Days 73–80)

**Scenario you build:** a model served on AKS whose drift triggers retraining with approval, an LLM evaluation gate in CI that stops bad prompts and models from shipping, a model cost comparison, a golden-path service template, and a FinOps review.

[← Back to tracker](../TRACKER.md)

---

<a id="day-73"></a>
### Day 73 · MLOps · Model serving: real-time and batch

**Time:** ~3 h

**Why it matters:** serving is where ML meets your platform skills, and most production ML failures happen here.

**Learn**
- **Inference modes:** real-time vs batch vs streaming, and choosing by latency need and cost.
- **Serving service:** FastAPI that loads the model once at startup, with input validation via the model signature.
- **Containers:** slim images for ML libraries; CPU vs GPU.
- **Safe rollout:** canary and shadow deployments for models.
- **Tooling:** KServe / Seldon awareness; latency budgets.

**Do**
- [ ] FastAPI scoring service loading `@champion` from MLflow at startup
- [ ] Helm-deploy it to AKS with HPA
- [ ] Batch scoring as a Kubernetes CronJob writing results to storage

**Interview questions**
1. **Batch or real-time inference?** — Real-time when a decision is needed within the request. Batch when results can be precomputed (nightly scores): cheaper and simpler.
2. **How do you canary a model?** — Route a small % of traffic (or shadow it) to the new version, compare business and technical metrics, then promote or roll back automatically.
3. **How do you serve 10 models efficiently?** — Multi-model serving, shared base images, autoscaling to zero for rare models, batching requests, right-sizing.

**Gotchas**
- Loading the model on every request.
- Training/serving skew: preprocessing differs between training and serving code. Keep it inside the model pipeline.
- Multi-GB images from heavy ML dependencies slow scaling.

**Scenario:** p95 latency of the scoring API jumped from 80 ms to 900 ms after a new model version. Investigate.

**Done when:** real-time and batch scoring both use the same registered model.

**Resources:** [MLflow model serving](https://mlflow.org/docs/latest/deployment/) · [KServe](https://kserve.github.io/website/)

---

<a id="day-74"></a>
### Day 74 · MLOps · Monitoring, drift and automated retraining

**Time:** ~3 h

**Why it matters:** "how do you know a model is still good?" is the defining MLOps question.

**Learn**
- **Drift types:** data drift (input distribution), concept drift (input → outcome relationship), prediction drift.
- **Statistics:** PSI, KS test, distribution comparisons.
- **Delayed labels:** monitoring with proxies until ground truth arrives.
- **Tooling:** Evidently reports; Azure ML model monitoring.
- **Retraining:** triggers, approval, feedback loops and their risks.

**Do**
- [ ] Scheduled drift job (Evidently) comparing last week's inputs with training data
- [ ] When drift passes the threshold, trigger the Day 70 training workflow automatically
- [ ] The new candidate waits for approval before deployment

**Interview questions**
1. **How do you detect model degradation before you have labels?** — Input and prediction drift, confidence distribution changes, business proxy metrics, and a small labelled sample reviewed by humans.
2. **Retrain on a schedule or on a trigger?** — Schedule when data changes steadily; trigger on drift or performance. Always gate deployment on evaluation.
3. **What is the risk of feedback loops?** — The model influences future data (e.g. only approved applicants get outcomes), which biases retraining. Use holdout groups and exploration.

**Gotchas**
- Drift doesn't always mean a performance drop, and stable inputs don't guarantee good performance.
- Retraining on drifted *bad* data (e.g. a pipeline bug) automates the damage.
- Too-sensitive drift alerts cause alert fatigue.

**Scenario:** a marketing campaign brings a new customer segment, and drift alerts fire daily. What do you do?

**Done when:** an induced drift (shifted synthetic data) triggers a retraining run end to end.

**Resources:** [Evidently docs](https://docs.evidentlyai.com/) · [Azure ML model monitoring](https://learn.microsoft.com/azure/machine-learning/concept-model-monitoring)

---

<a id="day-75"></a>
### Day 75 · AI · LLM evaluation as a CI gate

**Time:** ~3 h

**Why it matters:** teams that can prove an LLM change is safe ship faster, and interviewers ask exactly how.

**Learn**
- **Datasets:** golden Q&A, adversarial/red-team set, regression cases from production failures.
- **Metrics:** groundedness, relevance, correctness, safety, format adherence.
- **LLM-as-judge:** rubrics, calibration against human labels, position/verbosity bias.
- **Offline vs online evaluation;** regression thresholds.
- **Tools:** Microsoft Foundry (formerly Azure AI Foundry) evaluation, LangSmith, Ragas, promptfoo.

**Do**
- [ ] 50-case evaluation set (30 golden + 10 adversarial + 10 past failures)
- [ ] CI job on every PR touching prompts, retrieval or model config; fail if groundedness or correctness drops beyond a threshold
- [ ] Publish the evaluation report as a PR comment or artifact

**Interview questions**
1. **How do you test and release a prompt change safely?** — Version it → run the eval suite in CI → compare to baseline → shadow/A-B on live traffic → monitor → instant rollback.
2. **How reliable is LLM-as-judge?** — Useful at scale but biased. Calibrate it against human-labelled samples, use clear rubrics, prefer pairwise comparisons, and spot-check.
3. **What do you evaluate online, in production?** — User feedback, refusal/escalation rates, groundedness sampling, guardrail triggers, cost and latency per request.

**Gotchas**
- Tiny evaluation sets make the gate flip on noise.
- Using the same model as generator and judge inflates scores.
- Evaluation runs cost money, so cache results and run the full suite only on relevant changes.

**Scenario:** a PM wants to switch to a newer model tomorrow "because it's better". What's your process?

**Done when:** a deliberately bad prompt change fails CI.

**Resources:** [Microsoft Foundry (formerly Azure AI Foundry) evaluation](https://learn.microsoft.com/azure/ai-foundry/concepts/observability) · [promptfoo](https://www.promptfoo.dev/docs/intro/)

---

<a id="day-76"></a>
### Day 76 · AI · Model selection, cost and open models

**Time:** ~3 h

**Why it matters:** AI engineers are judged on picking the cheapest model that meets the bar and planning for model churn.

**Learn**
- **Comparing models:** quality on *your* evaluation set, latency, cost per 1,000 requests, context needs.
- **Cheaper options:** small models and routing; batch APIs for offline work.
- **Open-weight models:** Llama, Mistral, Phi and others via Ollama, Microsoft Foundry (formerly Azure AI Foundry) or Bedrock; licence terms.
- **Self-hosting economics:** GPU cost, utilisation, ops burden.
- **Model lifecycle:** versions, retirement dates, upgrade testing.

**Do**
- [ ] Run your evaluation set across 3 models (e.g. a large, a small and an open model)
- [ ] Table: quality score, p95 latency, cost per 1,000 requests
- [ ] Run one small open model locally with Ollama against the same 10 questions
- [ ] Write a one-page recommendation memo

**Interview questions**
1. **Recommend a model for an internal policy Q&A assistant.** — The smallest model that passes the evaluation bar with headroom; reasoning for the trade-offs; fallback to a larger model for complex queries.
2. **Should we self-host an open model?** — Yes if data must stay on-prem, usage is high and steady, or customisation is needed. No if usage is low or spiky (idle GPUs) and the team lacks GPU ops skills.
3. **How do you plan for model retirement?** — Track retirement dates, pin versions, keep the eval suite ready, test the successor early, and abstract providers behind a gateway.

**Gotchas**
- Public benchmarks don't predict performance on your data.
- Idle GPUs are the fastest way to waste budget.
- Open-weight licences vary: check commercial-use terms.

**Scenario:** the CFO asks why the AI feature costs USD 40k/month. Present options to halve it.

**Done when:** your memo recommends one model with numbers.

**Resources:** [Microsoft Foundry (formerly Azure AI Foundry) models](https://learn.microsoft.com/azure/ai-foundry/concepts/foundry-models-overview) · [Ollama](https://ollama.com/)

---

<a id="day-77"></a>
### Day 77 · DevOps · Platform engineering and golden paths

**Time:** ~3 h

**Why it matters:** platform-engineer roles are about developer experience at scale, not just tooling.

**Learn**
- **Internal developer platform:** self-service, golden paths, platform as a product.
- **Templates:** `dotnet new` templates, cookiecutter, the Backstage scaffolder (concepts).
- **Measuring:** DORA metrics (deployment frequency, lead time, change failure rate, time to restore).
- **Team Topologies:** platform team vs stream-aligned teams (awareness).

**Do**
- [ ] Template that scaffolds a new service with Dockerfile, Helm chart, pipeline, OpenTelemetry and dashboards
- [ ] Time it: from template to deployed in dev, in minutes
- [ ] Write a one-page "platform offering" for app teams

**Interview questions**
1. **What does a platform team give app teams?** — Paved roads: templates, CI/CD, environments, observability, security defaults, docs and support, consumed self-service.
2. **How do you know the platform is working?** — DORA metrics, time to first deploy for a new service, adoption rate, developer satisfaction, ticket volume.
3. **How do you drive adoption without mandates?** — Make the golden path the easiest path, migrate a willing team first, publish wins, and keep escape hatches.

**Gotchas**
- Building a portal before the paved roads exist.
- Mandating a platform that's slower than what teams do today.
- No product owner for the platform.

**Scenario:** teams take 3 weeks to get a new service into production. Get it to 1 day.

**Done when:** a brand-new service reaches dev from the template in under 30 minutes.

**Resources:** [platformengineering.org](https://platformengineering.org/) · [DORA research](https://dora.dev/)

---

<a id="day-78"></a>
### Day 78 · DevOps · FinOps: cloud and Kubernetes cost

**Time:** ~3 h

**Why it matters:** cost questions come up in every senior cloud and platform interview, and AI has made them bigger.

**Learn**
- **Cost drivers:** compute, storage, egress, NAT, logging, LLM tokens.
- **Levers:** rightsizing, autoscaling, scale-to-zero, spot nodes, reservations/savings plans.
- **Allocation:** tagging, showback/chargeback; Kubernetes cost allocation (AKS cost analysis, OpenCost).
- **Guardrails:** budgets and anomaly alerts.

**Do**
- [ ] Cost report by `CostCenter` tag
- [ ] Add a spot node pool for batch jobs (with tolerations)
- [ ] Reduce log ingestion by 30% without losing errors
- [ ] `docs/cost-estimate.md` for your platform per month

**Interview questions**
1. **How would you cut a cloud bill by 30%?** — Find the top 5 cost lines, remove idle resources, rightsize, autoscale, buy reservations for the steady baseline, reduce logging/egress, add tagging and accountability.
2. **How do you allocate Kubernetes costs to teams?** — Namespace per team, requests-based allocation, cost tooling (AKS cost analysis/OpenCost), showback reports.
3. **How do you control LLM costs?** — Gateway quotas, caching, routing to smaller models, prompt trimming, batch APIs, budgets per team.

**Gotchas**
- Spot nodes for stateful or critical workloads (evictions).
- Long reservations on workloads that are about to change.
- Hidden egress (cross-region, cross-cloud, NAT).

**Scenario:** non-prod environments cost more than prod. Fix it.

**Done when:** your monthly cost estimate is in the README with the top 3 savings levers.

**Resources:** [FinOps Foundation](https://www.finops.org/introduction/what-is-finops/) · [Azure Cost Management](https://learn.microsoft.com/azure/cost-management-billing/)

---

<a id="day-79"></a>
### Day 79 · .NET + Design · Classic case studies: notifications and payments

**Time:** ~3 h

**Why it matters:** these two come up often for enterprise and fintech roles.

**Learn**
- **Notification system:** fan-out, channels (email, SMS, push), user preferences, templates, retries, deduplication, rate limits, priority queues.
- **Payment system:** idempotency keys, double-entry ledger, state machine, external PSP integration, reconciliation, exactly-once *effects* via idempotency.
- **Reference:** the URL shortener from Day 7.

**Do**
- [ ] Two timed 45-minute designs with diagrams: notification system, payment system (`design/`)
- [ ] Self-review each against the framework from Day 7

**Interview questions**
1. **Design a notification system for 50 million users.** — Ingest API → queue → preference/template service → per-channel workers → providers; dedupe; retries with backoff; DLQ; rate limits; analytics.
2. **Design a payment processing system.** — Idempotent API, ledger as source of truth, state machine per payment, async PSP callbacks, reconciliation jobs, outbox for events, strong consistency where money moves.
3. **How do you guarantee a payment is never charged twice?** — Idempotency keys end to end, a unique constraint on the payment ID, idempotent PSP calls, and reconciliation to catch the rest.

**Gotchas**
- Forgetting non-functional requirements (latency, availability, compliance).
- No capacity numbers.
- Ignoring failure modes (provider down, timeout after charge).

**Scenario:** the PSP timed out, so you don't know if the customer was charged. What does your system do?

**Done when:** both designs include numbers, failure handling and trade-offs.

**Resources:** [System Design Primer](https://github.com/donnemartin/system-design-primer) · [ByteByteGo blog (free articles)](https://blog.bytebytego.com/)

---

<a id="day-80"></a>
### Day 80 · Build + Defend · Model and prompt lifecycle

**Time:** ~4 h

**Do**
- [ ] Model on AKS; drift triggers retraining; approval before deploy
- [ ] LLM evaluation gate in CI, with a failing example PR in your history
- [ ] Model comparison memo + cost estimate in the README
- [ ] Golden-path template used to create one new service
- [ ] Record answers to the three questions below

**Interview questions**
1. **How do you detect model degradation before you have labels?** — Your drift dashboard.
2. **How do you test and release a prompt change safely?** — Your CI gate, shown on a real PR.
3. **What does a platform team give app teams, and how do you know it's working?** — Your template and its time-to-deploy number.

**Gotchas**
- Don't let the evaluation gate become a flaky check people ignore. Fix flakiness immediately.

**Done when:** you can show one bad prompt and one bad model being stopped automatically.
