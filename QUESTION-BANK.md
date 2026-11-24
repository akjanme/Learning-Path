# Interview question bank

All 288 interview questions from the plan, grouped by track, each with its answer hint and a link to the day that teaches it. Practise out loud: cover the hint, answer in 3–5 minutes, then compare.

## Cloud

**Day 1 — [Azure landing zones and governance](sprints/sprint-01-secure-baseline.md#day-1)**

- [ ] How would you organise Azure for 20 application teams?
  - *Hint:* Use management groups by archetype (corp/online/sandbox), a subscription per workload per environment as the unit of isolation and scale, and policy plus RBAC at management-group level. Use subscription vending so teams get a ready subscription in hours, not weeks.
- [ ] What is the difference between Azure Policy and RBAC?
  - *Hint:* RBAC controls *who* can perform an action. Policy controls *what* configuration is allowed, whoever deploys it, even an Owner.
- [ ] When do you use DeployIfNotExists, and what does it need?
  - *Hint:* For auto-remediation such as diagnostic settings or private DNS records. The assignment needs a managed identity with the right roles, and existing resources need a remediation task.

**Day 2 — [Identity: Entra ID, RBAC, Managed Identity, Key Vault](sprints/sprint-01-secure-baseline.md#day-2)**

- [ ] Managed Identity vs service principal vs workload identity federation?
  - *Hint:* Use Managed Identity for workloads running in Azure: no secret to manage. Use a service principal with a certificate for systems outside Azure that can't federate. Use workload identity federation for GitHub Actions, Kubernetes and other identity providers: they swap a trusted token for an Entra token, again with no secret.
- [ ] System-assigned or user-assigned identity?
  - *Hint:* A system-assigned identity lives and dies with its resource. A user-assigned identity has its own lifecycle: you can grant it permissions before deployment and share it across instances. That suits blue-green, scale sets and recreated resources.
- [ ] What is the difference between the control plane and the data plane?
  - *Hint:* The control plane manages the resource (create, configure). The data plane is the content (blobs, secrets). Contributor on a storage account doesn't give Entra-based blob read access, but it can list the account keys.

**Day 9 — [Azure networking: VNets, NSGs, hub-spoke](sprints/sprint-02-private-ai-assistant.md#day-9)**

- [ ] Is VNet peering transitive? How do two spokes talk?
  - *Hint:* No. Route spoke-to-spoke traffic through a firewall or NVA in the hub using UDRs, use Virtual WAN, or peer the spokes directly if policy allows.
- [ ] NSG vs Azure Firewall?
  - *Hint:* An NSG is a distributed L3/L4 stateful filter on a subnet or NIC. Azure Firewall is a central L3–L7 service with FQDN filtering, threat intelligence, TLS inspection (Premium) and central logging. Enterprises use both.
- [ ] How do you plan IP addressing for 50 spokes plus on-premises?
  - *Hint:* Get a non-overlapping range from network/IPAM up front. Size spokes for growth (especially AKS) and keep a summary range per region.

**Day 10 — [Private Endpoints, private DNS, App Gateway, Front Door](sprints/sprint-02-private-ai-assistant.md#day-10)**

- [ ] Private endpoint vs service endpoint?
  - *Hint:* A private endpoint gives the resource a private IP and works from on-premises and peered VNets. A service endpoint keeps the public IP but restricts access to the subnet. Enterprises standardise on private endpoints.
- [ ] An app can't reach a resource over its private endpoint. How do you troubleshoot?
  - *Hint:* DNS first: does the FQDN resolve to the private IP *from the caller's VNet*? Then check the private DNS zone link, custom DNS forwarding to Azure DNS (168.63.129.16), NSG/UDR on the path, and public access settings.
- [ ] Front Door vs App Gateway: when do you use both?
  - *Hint:* Front Door for global entry, failover and edge WAF. App Gateway for regional L7 routing into private backends. Front Door → Private Link → backend is the common pattern.

**Day 17 — [Choosing compute: App Service, Container Apps, Functions, AKS](sprints/sprint-03-policy-document-qa.md#day-17)**

- [ ] Pick compute for (a) event-driven document processing, (b) a steady .NET API, (c) a 40-microservice platform.
  - *Hint:* (a) Functions or Container Apps jobs, (b) App Service or Container Apps, (c) AKS, or Container Apps if the teams don't need Kubernetes. Justify each by ops effort and scaling.
- [ ] How do you reduce cold starts?
  - *Hint:* Premium or Flex with always-ready instances, min replicas > 0 on Container Apps, smaller packages, avoiding heavy startup work.
- [ ] What does a slot swap actually swap?
  - *Hint:* Content and most settings. Settings marked "deployment slot setting" stay with the slot. Warm-up happens before the swap.

**Day 18 — [Messaging: Service Bus, Event Grid, Event Hubs](sprints/sprint-03-policy-document-qa.md#day-18)**

- [ ] Service Bus vs Event Grid vs Event Hubs, with a real example of each?
  - *Hint:* Service Bus: "approve mandate" command. Event Grid: "blob created" notification. Event Hubs: clickstream or IoT telemetry.
- [ ] How do you guarantee ordering?
  - *Hint:* Service Bus sessions (ordered per session ID) or Event Hubs partitions (ordered per partition key). Global ordering doesn't scale.
- [ ] Is delivery exactly once?
  - *Hint:* In practice it's at-least-once. Design idempotent consumers; duplicate detection helps only within its time window.

**Day 25 — [Azure SQL and Cosmos DB](sprints/sprint-04-permission-aware-rag.md#day-25)**

- [ ] Choose a partition key for chat history.
  - *Hint:* `userId` (or `tenantId+userId`): high cardinality, matches the access pattern, spreads writes. Avoid date as the key because it creates hot partitions.
- [ ] SQL or Cosmos DB for mandates, and why?
  - *Hint:* SQL: relational data, transactions across entities, reporting, strong consistency. Cosmos only if global scale or latency demands it.
- [ ] Explain Cosmos DB consistency levels.
  - *Hint:* From Strong through Bounded Staleness, Session, Consistent Prefix, to Eventual. Session gives read-your-writes per client and is the usual default.

**Day 26 — [Redis caching and data protection](sprints/sprint-04-permission-aware-rag.md#day-26)**

- [ ] How do you invalidate caches?
  - *Hint:* TTL for tolerable staleness, explicit eviction on writes (events), versioned keys. Never rely on "we'll clear it manually".
- [ ] What is a cache stampede and how do you prevent it?
  - *Hint:* Many requests miss at once and hit the DB. Prevent it with request coalescing/locks, early refresh and jittered TTLs.
- [ ] When is a semantic cache dangerous?
  - *Hint:* When answers depend on the user's permissions or personal data: one user's cached answer could be served to another.

**Day 33 — [AKS architecture: node pools, networking, upgrades](sprints/sprint-05-agent-on-aks.md#day-33)**

- [ ] Why separate system and user node pools?
  - *Hint:* To isolate critical system pods (CoreDNS, metrics) from app workloads and scale or size pools independently. Taint the system pool.
- [ ] Which AKS networking model and why?
  - *Hint:* Usually CNI Overlay: pods get IPs from an overlay range, saving VNet IPs, with good performance. Choose a VNet-routable pod IP only when external systems must reach pods directly.
- [ ] How do you do zero-downtime AKS upgrades?
  - *Hint:* PDBs, multiple replicas spread across zones, max surge, readiness probes, maintenance windows, and upgrading a non-prod cluster first.

**Day 34 — [AKS identity, ingress and autoscaling](sprints/sprint-05-agent-on-aks.md#day-34)**

- [ ] How does a pod access Azure resources without secrets?
  - *Hint:* Workload identity: Kubernetes issues a service-account token, Entra trusts the cluster's OIDC issuer via a federated credential, and the SDK exchanges the token for an Entra token.
- [ ] HPA vs KEDA vs cluster autoscaler?
  - *Hint:* HPA scales pods on metrics. KEDA scales pods on events (queues, streams), including to zero. The cluster autoscaler adds or removes nodes when pods can't be scheduled.
- [ ] Traffic spikes 10× at month-end. What scales, and how fast?
  - *Hint:* Pods scale in seconds, nodes in minutes, so you need headroom or overprovisioning. Pre-scale for known peaks, and check database and downstream limits.

**Day 41 — [Azure Monitor, Log Analytics, KQL, Application Insights](sprints/sprint-06-production-readiness.md#day-41)**

- [ ] What do you monitor for an API?
  - *Hint:* The RED metrics (rate, errors, duration) per endpoint, dependency health, saturation (CPU, memory, connection pools), business KPIs, and synthetic availability checks.
- [ ] How do you cut Log Analytics cost?
  - *Hint:* Drop noisy logs at the source, set log levels, use Basic/auxiliary plans for verbose tables, sampling, shorter retention, and data collection rules.
- [ ] How do you trace one request across services?
  - *Hint:* W3C trace context propagated through HTTP and messages, with a correlated operation ID in App Insights/OpenTelemetry.

**Day 42 — [High availability and disaster recovery](sprints/sprint-06-production-readiness.md#day-42)**

- [ ] Design DR for a banking app with a 15-minute RPO.
  - *Hint:* Zone-redundant primary; async geo-replication for data (SQL failover group, Cosmos multi-region); IaC to rebuild compute in the secondary; Front Door failover; tested runbooks; quarterly drills.
- [ ] Calculate a composite SLA.
  - *Hint:* Serial dependencies multiply: 99.95% × 99.99% ≈ 99.94%. Redundancy improves it; show the maths.
- [ ] What are the pitfalls of active-active?
  - *Hint:* Write conflicts, data consistency, double cost, complex testing, and hidden single points (one DNS, one identity provider).

**Day 49 — [Security posture: zero trust, Defender for Cloud, private AKS](sprints/sprint-07-secure-ai-gateway.md#day-49)**

- [ ] How do you apply zero trust on Azure?
  - *Hint:* Entra ID with Conditional Access and MFA, managed identities, private endpoints and segmentation, least-privilege RBAC with PIM, encryption, continuous monitoring with Defender/Sentinel.
- [ ] How do you prioritise 300 Defender recommendations?
  - *Hint:* By exploitability and exposure: internet-facing first, identity issues, critical data stores. Use the secure-score impact and fix by policy, not by hand.
- [ ] When do you need customer-managed keys?
  - *Hint:* When regulation or contracts require key control or revocation. CMK adds operational risk (key rotation, availability).

**Day 50 — [API Management as an AI gateway](sprints/sprint-07-secure-ai-gateway.md#day-50)**

- [ ] The Azure OpenAI bill tripled this month. What do you check and change?
  - *Hint:* Token metrics per app/feature through the gateway; find the runaway caller or prompt (longer contexts, loops, missing caching); then quotas, caching, routing to smaller models and budgets/alerts.
- [ ] How do you give 15 teams access to Azure OpenAI?
  - *Hint:* A central AI gateway with per-team products and quotas, Entra auth, logging, standard content filters, chargeback by token metrics, and private networking.
- [ ] How do you handle 429s across deployments?
  - *Hint:* Backend pool with priority or weighted routing, circuit breaker, retries honouring `retry-after`, PTU with pay-as-you-go spillover.

**Day 57 — [AWS foundations, mapped from Azure](sprints/sprint-08-aws-mcp-gitops.md#day-57)**

- [ ] How is an IAM policy evaluated?
  - *Hint:* Default deny. An explicit deny anywhere wins. Otherwise you need an allow from identity or resource policies, within SCPs and permission boundaries.
- [ ] Security group vs NACL?
  - *Hint:* A security group is stateful, at instance/ENI level, allow-only. A NACL is stateless, at subnet level, with allow and deny rules (remember ephemeral ports).
- [ ] How do you structure AWS accounts for an enterprise?
  - *Hint:* AWS Organizations with OUs (security, infrastructure, workloads, sandbox), an account per workload/environment, SCP guardrails, Control Tower for the landing zone.

**Day 58 — [AWS services for the app: ECS/EKS, Lambda, SQS/SNS, data, Bedrock](sprints/sprint-08-aws-mcp-gitops.md#day-58)**

- [ ] Azure Container Apps vs ECS Fargate vs EKS: when do you pick each?
  - *Hint:* Container Apps / Fargate for simple, serverless container ops. EKS/AKS for platform needs (operators, mesh, multi-tenant clusters).
- [ ] What goes wrong if the SQS visibility timeout is too short?
  - *Hint:* The message reappears while it's still being processed, so it's processed twice. Set the timeout above processing time, or extend it during processing.
- [ ] Bedrock or Azure OpenAI?
  - *Hint:* Model choice and availability, data residency, existing cloud and identity, enterprise agreements, guardrail features, latency to your data.

## AI

**Day 3 — [Python for a C# developer](sprints/sprint-01-secure-baseline.md#day-3)**

- [ ] What is the GIL and when does it matter?
  - *Hint:* In standard CPython only one thread runs Python bytecode at a time. CPU-bound threads don't run in parallel, so use multiprocessing or native libraries. I/O-bound work is fine with async or threads. (Free-threaded builds exist but are not the default.)
- [ ] When do you use Pydantic vs a dataclass?
  - *Hint:* Pydantic validates and coerces data from untrusted sources such as requests and LLM output. A dataclass is a lightweight internal container.
- [ ] How do you make Python dependencies reproducible?
  - *Hint:* Pin versions with a lock file (uv/Poetry), build containers from the lock file, and scan dependencies in CI.

**Day 4 — [FastAPI service and first LLM call](sprints/sprint-01-secure-baseline.md#day-4)**

- [ ] How does an app authenticate to Azure OpenAI without keys?
  - *Hint:* Give the app a Managed Identity with the `Cognitive Services OpenAI User` role and request tokens through the Azure Identity SDK. Disable key-based (local) auth on the resource.
- [ ] What drives the cost and latency of an LLM call?
  - *Hint:* Cost is input tokens + output tokens × the model's price. Latency is dominated by the number of output tokens and the model size, plus time to first token.
- [ ] How do you handle 429 (rate limit) errors?
  - *Hint:* Retry with exponential backoff that honours `retry-after`. Size quota (tokens and requests per minute) per deployment. Spread load across deployments or regions, often through a gateway.

**Day 11 — [LLM fundamentals that interviewers probe](sprints/sprint-02-private-ai-assistant.md#day-11)**

- [ ] Why do LLMs hallucinate, and how do you reduce it in an enterprise app?
  - *Hint:* They generate plausible tokens, not verified facts. Reduce it with grounding (RAG), instructions to answer only from context, citations, refusing when context is missing, constrained output, and evaluation.
- [ ] What drives the cost and latency of an LLM call?
  - *Hint:* Token counts, model size, output length and concurrency or quota. Mitigate with smaller models for simple steps, caching, shorter prompts and streaming.
- [ ] When would you choose a small model over a frontier model?
  - *Hint:* For classification, routing, extraction and high-volume, latency-sensitive tasks, once evaluation shows the quality is good enough.

**Day 12 — [Prompting, structured output and function calling](sprints/sprint-02-private-ai-assistant.md#day-12)**

- [ ] How do you make LLM output reliably machine-parseable?
  - *Hint:* Schema-constrained structured outputs, validation at the boundary, a bounded retry with the error message, and a safe fallback path.
- [ ] Who executes a function call, the model or your application, and why does it matter?
  - *Hint:* Your application. Authorization, input validation and side effects must be enforced in your code with the *user's* permissions, never trusted to the model.
- [ ] How do you test prompts?
  - *Hint:* Keep a fixed test set with expected properties, run it in CI on every prompt or model change, and track scores over time.

**Day 19 — [Chunking, embeddings and Azure AI Search indexing](sprints/sprint-03-policy-document-qa.md#day-19)**

- [ ] How do you choose chunk size?
  - *Hint:* Small chunks give precise retrieval but lose context. Large chunks keep context but add noise and cost. Choose by document structure, then *measure* with an evaluation set.
- [ ] What happens when you change the embedding model?
  - *Hint:* Re-embed and reindex everything, because vectors from different models aren't comparable. Run the new index side by side, then switch.
- [ ] Azure AI Search vs pgvector vs a dedicated vector DB?
  - *Hint:* AI Search: hybrid search, semantic ranking, security filters, managed. pgvector: simple when Postgres is already the system of record. Dedicated DBs: very large scale or special features.

**Day 20 — [RAG v1 with citations and "I don't know"](sprints/sprint-03-policy-document-qa.md#day-20)**

- [ ] How do you reduce hallucinations in RAG?
  - *Hint:* Better retrieval, strict grounding instructions, citations tied to chunk IDs, refusal when evidence is weak, and groundedness evaluation.
- [ ] How do you handle follow-up questions?
  - *Hint:* Rewrite them into standalone queries using chat history, then retrieve. Don't just append the history to the search.
- [ ] How many chunks do you put in context?
  - *Hint:* As few as give good answers. Tune k with evaluation; more chunks often lowers quality and raises cost.

**Day 27 — [Advanced retrieval: hybrid search, semantic ranking, query rewriting](sprints/sprint-04-permission-aware-rag.md#day-27)**

- [ ] Why does hybrid search beat vector-only for enterprise documents?
  - *Hint:* Exact terms (policy numbers, product codes, names) are matched well by keyword search and poorly by embeddings. Hybrid gets both meaning and exact matches.
- [ ] What does a reranker do and what does it cost?
  - *Hint:* It re-scores the top-N candidates with a stronger model for better precision, adding latency and per-query cost.
- [ ] How do you choose k?
  - *Hint:* Empirically: plot quality against k on your evaluation set, and balance it against context cost and latency.

**Day 28 — [Security trimming and RAG evaluation](sprints/sprint-04-permission-aware-rag.md#day-28)**

- [ ] HR documents must only be visible to HR. How do you enforce that in RAG?
  - *Hint:* Store ACLs per chunk at ingestion and filter at query time with the user's identity, inside the search query itself. Never rely on the prompt. Test it with negative cases.
- [ ] RAG answers are wrong 20% of the time. How do you tell whether retrieval or generation is at fault?
  - *Hint:* Measure retrieval separately: was the right chunk in the context? If yes, it's a generation or prompt issue. If no, fix chunking, search or the query.
- [ ] How do you build a golden evaluation dataset?
  - *Hint:* Real user questions plus SME-written answers and sources, edge cases and adversarial prompts, versioned and refreshed regularly.

**Day 35 — [Tool calling and the agent loop, from scratch](sprints/sprint-05-agent-on-aks.md#day-35)**

- [ ] When do you use an agent, and when a fixed workflow?
  - *Hint:* A workflow when the steps are known: cheaper, testable, predictable. An agent when the steps depend on the input and can't be enumerated. Many good systems are workflows with small agentic steps.
- [ ] How do you stop runaway loops and cost?
  - *Hint:* Iteration and token budgets, timeouts, loop detection, and fallback to a human.
- [ ] How do you control what tools an agent can do?
  - *Hint:* Least-privilege tools, authorization with the user's identity inside each tool, and confirmation for side-effecting actions.

**Day 36 — [LangGraph: stateful agents with human approval](sprints/sprint-05-agent-on-aks.md#day-36)**

- [ ] Why model an agent as a graph?
  - *Hint:* Explicit control flow, inspectable state, deterministic edges where possible, and easy insertion of approvals and retries.
- [ ] How does an approval that happens two days later resume the run?
  - *Hint:* Persisted state in a checkpointer keyed by thread ID. The approval event resumes the graph from the interrupt.
- [ ] How do you test agents?
  - *Hint:* Unit-test nodes with mocked LLMs and tools, use scenario tests on recorded cases, run evaluations on trajectories, and keep end-to-end tests few but realistic.

**Day 43 — [LLM tracing, token cost and latency](sprints/sprint-06-production-readiness.md#day-43)**

- [ ] The AI assistant is slow. How do you find where the time goes?
  - *Hint:* Look at the trace waterfall: retrieval vs LLM (time to first token, output length) vs tools. Fix the biggest contributor first.
- [ ] How do you track LLM cost per tenant?
  - *Hint:* Tag every call with tenant/feature, record usage tokens, multiply by price in the pipeline or dashboard, and set budgets and alerts.
- [ ] Should you log prompts and responses?
  - *Hint:* Only with a policy: redact PII, separate secure store, retention limits, access controls. Log metadata by default.

**Day 44 — [Latency optimisation and prompt management](sprints/sprint-06-production-readiness.md#day-44)**

- [ ] How would you cut AI response latency by 50%?
  - *Hint:* Stream, route simple requests to small models, trim context, cache, parallelise retrieval and tools, and cap output length. Measure time to first token separately.
- [ ] How do you release a prompt change safely?
  - *Hint:* Version it, run the eval suite in CI, shadow or A/B test on a slice of traffic, monitor quality metrics, and keep instant rollback to the previous version.
- [ ] PTU or pay-as-you-go?
  - *Hint:* PTU for steady, high, latency-sensitive load (predictable performance and cost). Pay-as-you-go for spiky or early-stage workloads, often with spillover between them.

**Day 51 — [OWASP Top 10 for LLM apps and prompt injection](sprints/sprint-07-secure-ai-gateway.md#day-51)**

- [ ] A user tricks the assistant into revealing another customer's data. What failed?
  - *Hint:* Authorization: retrieval or tools weren't scoped to the user's identity. The prompt is never a security boundary.
- [ ] What is indirect prompt injection, and how do you defend against it?
  - *Hint:* Malicious instructions inside retrieved content. Treat all content as untrusted data, separate it clearly, limit tool permissions, require approval for actions, and filter with Prompt Shields-style detectors.
- [ ] What is "excessive agency"?
  - *Hint:* Giving an LLM tools or permissions beyond what the task needs. Reduce tool scope, add approvals, and use read-only defaults.

**Day 52 — [Guardrails: Content Safety, PII, output validation, human oversight](sprints/sprint-07-secure-ai-gateway.md#day-52)**

- [ ] What guardrail layers would you put on a customer-facing assistant?
  - *Hint:* Identity and authorization, input filtering, grounding, output filtering/validation, action approvals, monitoring and feedback, incident response.
- [ ] How do you handle guardrail false positives?
  - *Hint:* Measure them, tune thresholds per category, give a clear user message and a human escalation path, and review blocked samples.
- [ ] A regulator asks how a specific AI decision was made. What can you show?
  - *Hint:* The trace: inputs (redacted), retrieved sources, prompt version, model version, outputs, guardrail results, approver.

**Day 59 — [Model Context Protocol (MCP)](sprints/sprint-08-aws-mcp-gitops.md#day-59)**

- [ ] MCP vs plain function calling?
  - *Hint:* Function calling is the model-side mechanism. MCP is a standard protocol to package and expose tools/resources so any compatible client can use them, decoupling integrations from one app.
- [ ] How do you secure a remote MCP server?
  - *Hint:* OAuth with audience-validated tokens, per-user authorization inside each tool, least-privilege tools, rate limits, audit logs, and allow-listed clients.
- [ ] How do you let an LLM call internal systems safely?
  - *Hint:* Narrow, typed tools; the user's identity enforced by the backend; approvals for writes; input validation; logging; no raw database or shell access.

**Day 60 — [AI in .NET: Microsoft.Extensions.AI and Semantic Kernel](sprints/sprint-08-aws-mcp-gitops.md#day-60)**

- [ ] Should AI features live in the .NET service or a separate Python service?
  - *Hint:* Simple completions, summarisation and tool calls fit well in .NET (one stack, one deploy). Heavy RAG/agent/ML ecosystems and fast-moving libraries favour Python. Decide by team skills and ownership.
- [ ] How do you avoid vendor lock-in in AI code?
  - *Hint:* Abstractions (`IChatClient`), prompts and config outside code, evaluation suites to validate a model switch, a gateway in front of providers.
- [ ] How do you test AI code in .NET?
  - *Hint:* Mock `IChatClient` for unit tests, contract tests on structured outputs, evaluation tests against a fixed dataset.

**Day 68 — [Document Intelligence and human review](sprints/sprint-09-mlops-document-pipeline.md#day-68)**

- [ ] OCR/extraction service or LLM-based extraction?
  - *Hint:* Use a specialised service for high-volume, standard forms with confidence scores and lower cost. Use LLMs for messy, variable documents and reasoning. Often combine them: layout first, LLM second.
- [ ] How do you handle low-confidence results?
  - *Hint:* Per-field thresholds, human review queues, feedback into retraining, and tracking accuracy over time.
- [ ] How do you scale to 100,000 documents a day?
  - *Hint:* Async batch processing via queues, parallel workers, rate-limit awareness, retries, idempotent processing, and cost monitoring.

**Day 69 — [Multi-agent patterns, and fine-tuning vs RAG vs prompting](sprints/sprint-09-mlops-document-pipeline.md#day-69)**

- [ ] When would you fine-tune instead of using RAG?
  - *Hint:* Fine-tune for consistent format, style or a narrow task, or to shrink a model. Use RAG for knowledge that changes or must be cited. Fine-tuning is a poor way to add facts.
- [ ] When is a multi-agent system worth it?
  - *Hint:* When sub-tasks need different tools, prompts or permissions and can be evaluated separately. Otherwise one agent or a workflow is cheaper and more reliable.
- [ ] How do you evaluate a multi-agent system?
  - *Hint:* Per-agent evaluations, end-to-end task success, trajectory checks, and cost/latency per task.

**Day 75 — [LLM evaluation as a CI gate](sprints/sprint-10-model-and-prompt-lifecycle.md#day-75)**

- [ ] How do you test and release a prompt change safely?
  - *Hint:* Version it → run the eval suite in CI → compare to baseline → shadow/A-B on live traffic → monitor → instant rollback.
- [ ] How reliable is LLM-as-judge?
  - *Hint:* Useful at scale but biased. Calibrate it against human-labelled samples, use clear rubrics, prefer pairwise comparisons, and spot-check.
- [ ] What do you evaluate online, in production?
  - *Hint:* User feedback, refusal/escalation rates, groundedness sampling, guardrail triggers, cost and latency per request.

**Day 76 — [Model selection, cost and open models](sprints/sprint-10-model-and-prompt-lifecycle.md#day-76)**

- [ ] Recommend a model for an internal policy Q&A assistant.
  - *Hint:* The smallest model that passes the evaluation bar with headroom; reasoning for the trade-offs; fallback to a larger model for complex queries.
- [ ] Should we self-host an open model?
  - *Hint:* Yes if data must stay on-prem, usage is high and steady, or customisation is needed. No if usage is low or spiky (idle GPUs) and the team lacks GPU ops skills.
- [ ] How do you plan for model retirement?
  - *Hint:* Track retirement dates, pin versions, keep the eval suite ready, test the successor early, and abstract providers behind a gateway.

## DevOps

**Day 5 — [Git workflows and Linux essentials](sprints/sprint-01-secure-baseline.md#day-5)**

- [ ] Trunk-based or GitFlow for microservices with CI/CD, and why?
  - *Hint:* Trunk-based: short-lived branches, feature flags, frequent small merges. GitFlow's long-lived branches slow down continuous delivery.
- [ ] Revert or reset on a shared branch?
  - *Hint:* Revert, because it adds a new commit that undoes the change. Reset rewrites history and breaks everyone who already pulled.
- [ ] A service fails to start after a reboot. How do you troubleshoot?
  - *Hint:* `systemctl status`, `journalctl -u <svc> -b`, check the unit file and its dependencies, permissions, port conflicts and environment differences.

**Day 6 — [Docker fundamentals](sprints/sprint-01-secure-baseline.md#day-6)**

- [ ] ENTRYPOINT vs CMD?
  - *Hint:* ENTRYPOINT is the executable. CMD supplies default arguments that `docker run` can override. Use exec (JSON) form so signals reach the process.
- [ ] How do you make image builds faster?
  - *Hint:* Order layers from least to most frequently changed. Copy `*.csproj`/lock files and restore before copying source. Use BuildKit cache mounts and a good `.dockerignore`.
- [ ] Container vs VM?
  - *Hint:* Containers share the host kernel: process isolation, fast start, small footprint. VMs virtualise hardware with a full OS: stronger isolation, heavier.

**Day 13 — [Production-grade images, ACR and scanning](sprints/sprint-02-private-ai-assistant.md#day-13)**

- [ ] How do you keep container images secure over time?
  - *Hint:* Minimal bases, scanning in CI *and* in the registry, scheduled rebuilds to pick up base-image patches, and an SLA for fixing critical CVEs.
- [ ] Tag or digest: which do you deploy?
  - *Hint:* A digest is immutable. Tags can move. Use SHA tags for humans and pin by digest for strict environments.
- [ ] How does a cluster pull from a private registry without passwords?
  - *Hint:* The kubelet/managed identity is granted `AcrPull` (AKS attach-ACR), with the registry reached over a private endpoint.

**Day 14 — [Bash, Azure CLI automation and network troubleshooting](sprints/sprint-02-private-ai-assistant.md#day-14)**

- [ ] What does `set -euo pipefail` do?
  - *Hint:* Exit on error, error on unset variables, and fail a pipeline if any command in it fails.
- [ ] "Connection timed out" vs "connection refused"?
  - *Hint:* Timed out: packets dropped (NSG, firewall, routing). Refused: the host is reachable but nothing is listening on that port.
- [ ] How do you debug a TLS handshake failure?
  - *Hint:* `openssl s_client -connect host:443 -servername host`: check the certificate chain, SNI, protocol versions, expiry, and whether a proxy intercepts TLS.

**Day 21 — [Terraform fundamentals](sprints/sprint-03-policy-document-qa.md#day-21)**

- [ ] What is Terraform state and why does it exist?
  - *Hint:* The mapping between your config and real resource IDs, plus cached attributes. Terraform uses it to compute diffs. It holds secrets, so protect it.
- [ ] `count` vs `for_each`?
  - *Hint:* `count` is indexed, so removing an item shifts the indexes and recreates resources. `for_each` is keyed and stable.
- [ ] The plan wants to destroy and recreate a database. Why, and what do you do?
  - *Hint:* An attribute that forces replacement changed, or a resource address changed. Stop, check the diff, use `moved` blocks for renames, and add `prevent_destroy` on critical resources.

**Day 22 — [Terraform at team scale: backends, modules, drift, PR plans](sprints/sprint-03-policy-document-qa.md#day-22)**

- [ ] Someone changed a resource in the portal. What happens next, and what do you do?
  - *Hint:* The next plan shows drift and will revert it. Decide whether the change was intended: codify it, or let Terraform revert it. Then prevent recurrences with RBAC and policy.
- [ ] Workspaces or separate folders for dev/test/prod?
  - *Hint:* Separate folders and backends (or a wrapper tool) for strong isolation and different permissions. Workspaces suit identical, low-risk copies.
- [ ] How do you structure Terraform for 20 teams?
  - *Hint:* Shared, versioned platform modules; each team owns its own root configs and state; PR plans; policy checks; least-privilege pipeline identities per environment.

**Day 29 — [GitHub Actions with OIDC](sprints/sprint-04-permission-aware-rag.md#day-29)**

- [ ] Why OIDC instead of stored service principal secrets?
  - *Hint:* No long-lived secret to leak or rotate. Tokens are short-lived and scoped to a repo, branch or environment through the federation subject.
- [ ] How do you standardise pipelines across 30 repositories?
  - *Hint:* Reusable workflows in a central repo, versioned, with inputs; required checks and rulesets at org level.
- [ ] How do you secure self-hosted runners?
  - *Hint:* Ephemeral runners, isolated networks, no reuse across trust levels, and never running them for public-repo PRs.

**Day 30 — [Azure DevOps pipelines and CI/CD design at scale](sprints/sprint-04-permission-aware-rag.md#day-30)**

- [ ] Design CI/CD for 30 microservices owned by 6 teams.
  - *Hint:* Per-service pipelines from shared templates; build once, sign and scan; promote by environment with gates; trunk-based development; feature flags; GitOps for deploy; DORA metrics.
- [ ] Why promote one artifact instead of rebuilding per environment?
  - *Hint:* So what you tested is exactly what you deploy. Rebuilding introduces drift.
- [ ] What is your rollback strategy?
  - *Hint:* Redeploy the previous artifact (or revert in GitOps), with backward-compatible DB migrations (expand/contract) so rollback is safe.

**Day 37 — [Kubernetes core objects](sprints/sprint-05-agent-on-aks.md#day-37)**

- [ ] Liveness vs readiness vs startup probes?
  - *Hint:* Readiness: can it take traffic (removed from the Service if not). Liveness: is it stuck (restart it). Startup: protects slow starters from liveness kills.
- [ ] Requests vs limits?
  - *Hint:* Requests are used for scheduling and guaranteed capacity. Limits cap usage: memory over the limit gets OOMKilled, CPU over the limit gets throttled.
- [ ] How does a Service find its pods?
  - *Hint:* Its label selector matches pod labels; endpoints are created for *ready* pods only.

**Day 38 — [Helm and Kubernetes troubleshooting](sprints/sprint-05-agent-on-aks.md#day-38)**

- [ ] A pod is in CrashLoopBackOff in production. What are your first five commands?
  - *Hint:* `kubectl get pod -o wide`, `describe pod`, `logs --previous`, `get events --sort-by=.lastTimestamp`, then check config/secrets and recent deploys.
- [ ] What makes a pod Pending?
  - *Hint:* Not enough CPU/memory for its requests, node selectors or taints, an unbound PVC or zone mismatch, quota limits.
- [ ] Helm or Kustomize?
  - *Hint:* Helm for packaging, templating and releases; Kustomize for patching plain YAML per environment. Many teams use Helm charts with GitOps.

**Day 45 — [Prometheus, Grafana and OpenTelemetry on Kubernetes](sprints/sprint-06-production-readiness.md#day-45)**

- [ ] RED vs USE?
  - *Hint:* RED (rate, errors, duration) for request-driven services. USE (utilisation, saturation, errors) for resources such as CPU, disk and pools.
- [ ] How do you compute p95 latency in Prometheus?
  - *Hint:* `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`.
- [ ] Metrics vs logs vs traces: when do you use each?
  - *Hint:* Metrics for alerting and trends (cheap). Traces for where time goes. Logs for detailed context on specific events.

**Day 46 — [SLOs, alerting and incident response](sprints/sprint-06-production-readiness.md#day-46)**

- [ ] What SLOs would you set for an LLM-backed service?
  - *Hint:* Availability, p95 time to first token, end-to-end latency, plus quality SLIs such as groundedness rate and refusal rate. Explain why LLM latency varies (output length, provider load).
- [ ] It's 2 a.m. and the assistant is slow. Walk me through it.
  - *Hint:* Acknowledge and assess impact; check dashboards and recent changes; trace a slow request; mitigate first (roll back, fail over, route to a smaller model); communicate; postmortem.
- [ ] What makes a good postmortem?
  - *Hint:* Blameless, a timeline, root cause *and* contributing factors, what went well, owned and dated action items.

**Day 53 — [DevSecOps and the software supply chain](sprints/sprint-07-secure-ai-gateway.md#day-53)**

- [ ] How do you secure the software supply chain from commit to cluster?
  - *Hint:* Protected branches and reviews, SAST/SCA/secret scanning, pinned dependencies, hermetic builds, SBOMs, signing, admission policies that verify signatures, and runtime monitoring.
- [ ] A critical CVE has no fix yet. What do you do?
  - *Hint:* Assess exploitability in your context, mitigate (WAF rule, config change, network restriction), accept the risk formally with an expiry, and track it.
- [ ] A secret leaked in a public repo. What happens next?
  - *Hint:* Revoke/rotate immediately, check access logs, purge history, root-cause it, enable push protection.

**Day 54 — [Policy as code for Kubernetes and Terraform](sprints/sprint-07-secure-ai-gateway.md#day-54)**

- [ ] How do you enforce standards across 20 teams' clusters?
  - *Hint:* A policy library in Git, assigned centrally (Azure Policy initiative or Kyverno via GitOps), audit first then enforce, with exemptions tracked.
- [ ] How do you roll out a new policy without breaking production?
  - *Hint:* Audit mode, report violations, give teams time and fixes, then enforce, starting in non-prod.
- [ ] How do you segment network traffic inside Kubernetes?
  - *Hint:* NetworkPolicies per namespace (default-deny + explicit allows), plus a service mesh for mTLS and L7 policy if needed.

**Day 61 — [Terraform for multiple environments and clouds](sprints/sprint-08-aws-mcp-gitops.md#day-61)**

- [ ] How do you structure Terraform for multiple teams and environments?
  - *Hint:* Shared versioned modules, separate state per environment and component, PR plans, policy checks, environment-scoped pipeline identities.
- [ ] How do you promote an infrastructure change safely?
  - *Hint:* Version the module, apply to dev, test, then bump the version in prod with plan review and approval.
- [ ] Is a single multi-cloud module a good idea?
  - *Hint:* Usually not: lowest-common-denominator features and leaky abstractions. Standardise the interface and conventions, not the implementation.

**Day 62 — [GitOps with Argo CD and progressive delivery](sprints/sprint-08-aws-mcp-gitops.md#day-62)**

- [ ] Push-based CI/CD vs GitOps?
  - *Hint:* Push: the pipeline has cluster credentials and pushes changes. GitOps: an in-cluster agent pulls from Git and reconciles. No cluster credentials in CI, drift is corrected, and Git is the audit log.
- [ ] How do you roll back in GitOps?
  - *Hint:* Revert the commit and let Argo sync, or let Rollouts abort the canary automatically on bad metrics.
- [ ] How do you handle secrets with GitOps?
  - *Hint:* External Secrets / CSI driver pulling from Key Vault. Git holds references, never values.

**Day 70 — [CI/CD for machine learning](sprints/sprint-09-mlops-document-pipeline.md#day-70)**

- [ ] What should trigger retraining?
  - *Hint:* A schedule for slowly changing data, drift or performance alerts, new labelled data volume, or a code change. Always gated by evaluation.
- [ ] How do you gate a model release?
  - *Hint:* Beats the champion on the holdout set, passes sanity and fairness checks, latency within budget, human approval for high-risk models.
- [ ] What does "CI for data" mean?
  - *Hint:* Schema, range, null and distribution checks on incoming data before training or scoring.

**Day 77 — [Platform engineering and golden paths](sprints/sprint-10-model-and-prompt-lifecycle.md#day-77)**

- [ ] What does a platform team give app teams?
  - *Hint:* Paved roads: templates, CI/CD, environments, observability, security defaults, docs and support, consumed self-service.
- [ ] How do you know the platform is working?
  - *Hint:* DORA metrics, time to first deploy for a new service, adoption rate, developer satisfaction, ticket volume.
- [ ] How do you drive adoption without mandates?
  - *Hint:* Make the golden path the easiest path, migrate a willing team first, publish wins, and keep escape hatches.

**Day 78 — [FinOps: cloud and Kubernetes cost](sprints/sprint-10-model-and-prompt-lifecycle.md#day-78)**

- [ ] How would you cut a cloud bill by 30%?
  - *Hint:* Find the top 5 cost lines, remove idle resources, rightsize, autoscale, buy reservations for the steady baseline, reduce logging/egress, add tagging and accountability.
- [ ] How do you allocate Kubernetes costs to teams?
  - *Hint:* Namespace per team, requests-based allocation, cost tooling (AKS cost analysis/OpenCost), showback reports.
- [ ] How do you control LLM costs?
  - *Hint:* Gateway quotas, caching, routing to smaller models, prompt trimming, batch APIs, budgets per team.

## MLOps

**Day 65 — [ML fundamentals with scikit-learn](sprints/sprint-09-mlops-document-pipeline.md#day-65)**

- [ ] Precision or recall for fraud/risk detection?
  - *Hint:* It depends on cost. Missing fraud (low recall) is usually costlier, but too many false alarms (low precision) overload reviewers. Pick the threshold from business cost.
- [ ] How do you handle imbalanced data?
  - *Hint:* Use the right metrics (PR-AUC, recall at fixed precision), class weights, resampling, threshold tuning. Never rely on accuracy.
- [ ] Give an example of data leakage.
  - *Hint:* Scaling or imputing on the full dataset before the split, or a feature that's only known after the outcome (such as "account closed date").

**Day 66 — [Experiment tracking and model registry with MLflow](sprints/sprint-09-mlops-document-pipeline.md#day-66)**

- [ ] How do you reproduce a prediction from six months ago?
  - *Hint:* Model version → run ID → code commit, data version/snapshot, environment and parameters, all recorded at training time.
- [ ] How do models get promoted?
  - *Hint:* Register a candidate, evaluate it against the champion on a fixed test set plus business checks, get approval, move the alias, and deploy from the alias.
- [ ] Why use experiment tracking at all?
  - *Hint:* Comparability, reproducibility, collaboration, and an audit trail of which model was trained how.

**Day 67 — [Azure Machine Learning: jobs, pipelines, managed endpoints](sprints/sprint-09-mlops-document-pipeline.md#day-67)**

- [ ] Managed online endpoints or self-hosting on AKS?
  - *Hint:* Managed: less ops, built-in blue/green, monitoring, scaling. AKS: more control, shared platform, potentially cheaper at scale, custom runtimes.
- [ ] How do you do blue/green for models?
  - *Hint:* Two deployments behind one endpoint, shift traffic gradually while comparing metrics, keep instant rollback, use mirrored (shadow) traffic for risk-free tests.
- [ ] How do you secure an Azure ML workspace?
  - *Hint:* Private endpoints/managed VNet, managed identities, RBAC, no public compute IPs, Key Vault for secrets, data access through identity.

**Day 73 — [Model serving: real-time and batch](sprints/sprint-10-model-and-prompt-lifecycle.md#day-73)**

- [ ] Batch or real-time inference?
  - *Hint:* Real-time when a decision is needed within the request. Batch when results can be precomputed (nightly scores): cheaper and simpler.
- [ ] How do you canary a model?
  - *Hint:* Route a small % of traffic (or shadow it) to the new version, compare business and technical metrics, then promote or roll back automatically.
- [ ] How do you serve 10 models efficiently?
  - *Hint:* Multi-model serving, shared base images, autoscaling to zero for rare models, batching requests, right-sizing.

**Day 74 — [Monitoring, drift and automated retraining](sprints/sprint-10-model-and-prompt-lifecycle.md#day-74)**

- [ ] How do you detect model degradation before you have labels?
  - *Hint:* Input and prediction drift, confidence distribution changes, business proxy metrics, and a small labelled sample reviewed by humans.
- [ ] Retrain on a schedule or on a trigger?
  - *Hint:* Schedule when data changes steadily; trigger on drift or performance. Always gate deployment on evaluation.
- [ ] What is the risk of feedback loops?
  - *Hint:* The model influences future data (e.g. only approved applicants get outcomes), which biases retraining. Use holdout groups and exploration.

## .NET + Design

**Day 7 — [Clean Architecture refresh and design-interview framework](sprints/sprint-01-secure-baseline.md#day-7)**

- [ ] Microservices or modular monolith for a new product with one team?
  - *Hint:* A modular monolith: clear module boundaries, one deployment, easy to split later. Microservices add operational cost that one team can't absorb.
- [ ] What belongs in the domain layer?
  - *Hint:* Entities, value objects, aggregates, domain events and business rules. No EF, HTTP or infrastructure concerns.
- [ ] Estimate storage for 100 million short URLs over 5 years.
  - *Hint:* About 500 bytes per record (URL, key, metadata) × 100M ≈ 50 GB before replicas and indexes. State your assumptions out loud.

**Day 15 — [API design, gateways, load balancing, rate limiting](sprints/sprint-02-private-ai-assistant.md#day-15)**

- [ ] How do you make a POST idempotent?
  - *Hint:* The client sends an idempotency key. The server stores key → result atomically and returns the stored result on retries.
- [ ] Design a distributed rate limiter.
  - *Hint:* Token bucket per client in Redis with atomic Lua or `INCR` + TTL. Decide fail-open vs fail-closed, return 429 with `Retry-After`, and consider local plus global limits.
- [ ] How do you ship a breaking API change with 40 consumers?
  - *Hint:* A new version alongside the old, a deprecation policy and headers, usage telemetry per consumer, and a migration window before you remove the old one.

**Day 23 — [Messaging patterns: outbox, idempotency, DLQs](sprints/sprint-03-policy-document-qa.md#day-23)**

- [ ] What is the dual-write problem and how do you solve it?
  - *Hint:* A DB commit followed by a failed publish (or the reverse) leaves inconsistent state. Fix it with the transactional outbox or change data capture.
- [ ] How do you guarantee customers never get duplicate emails?
  - *Hint:* An idempotent consumer keyed on a business ID, deduplication storage, and at-least-once delivery accepted upstream.
- [ ] How do you preserve order per customer while scaling consumers?
  - *Hint:* Partition or session by customer ID so one consumer handles one customer's messages at a time.

**Day 31 — [Caching, database choice, partitioning](sprints/sprint-04-permission-aware-rag.md#day-31)**

- [ ] How do you choose a shard key?
  - *Hint:* High cardinality, even distribution, matches the main access pattern, avoids cross-shard queries for hot paths.
- [ ] Read replica or cache: which and when?
  - *Hint:* A cache for hot, tolerant-of-staleness reads with low latency. Replicas for offloading complex read queries. Both lag.
- [ ] How do you provide read-your-writes with replicas?
  - *Hint:* Read from the primary for a short window after the user's write, use session tokens, or route by user.

**Day 39 — [Resilience patterns](sprints/sprint-05-agent-on-aks.md#day-39)**

- [ ] What is a retry storm and how do you avoid it?
  - *Hint:* Retries at many layers multiply traffic during an outage. Retry at one layer, add jitter, cap attempts, and use circuit breakers and retry budgets.
- [ ] What are the circuit breaker states?
  - *Hint:* Closed (normal), open (fail fast), half-open (trial requests to test recovery).
- [ ] Where do timeouts belong?
  - *Hint:* On every outbound call, shorter than the caller's own timeout, with an overall request deadline.

**Day 47 — [Observability design in .NET](sprints/sprint-06-production-readiness.md#day-47)**

- [ ] How do you trace across asynchronous messaging?
  - *Hint:* Inject trace context into message properties on publish and extract it on consume, creating linked spans.
- [ ] How do you design observability for 30 services?
  - *Hint:* Standard telemetry library/template, OpenTelemetry everywhere, central backends, naming conventions, golden dashboards per service, SLOs per user journey.
- [ ] When do you use logs vs traces?
  - *Hint:* Traces for flow and timing across services; logs for detailed events, correlated by trace ID.

**Day 55 — [OAuth2/OIDC and Entra ID in ASP.NET Core](sprints/sprint-07-secure-ai-gateway.md#day-55)**

- [ ] Which OAuth flow for a SPA, a nightly batch job, and an API calling another API as the user?
  - *Hint:* Auth code + PKCE; client credentials (or managed identity); on-behalf-of.
- [ ] How does your AI service call internal APIs with the user's permissions?
  - *Hint:* On-behalf-of token exchange, so the downstream API authorizes the actual user, not the AI service's broad identity.
- [ ] ID token vs access token?
  - *Hint:* The ID token is for the client, to learn who logged in. The access token is for the API, to authorize calls. Never use ID tokens to call APIs.

**Day 63 — [Event-driven design, sagas, CQRS and migration strategy](sprints/sprint-08-aws-mcp-gitops.md#day-63)**

- [ ] Migrate a 10-year-old on-prem .NET app to the cloud: which R, and in what order?
  - *Hint:* Assess, then usually rehost/replatform first for quick wins (containers, managed DB), then refactor the hot spots with the strangler fig. Retire what's unused.
- [ ] Choreography or orchestration for a saga?
  - *Hint:* Choreography for a few simple steps (loose coupling). Orchestration for complex flows needing visibility, timeouts and compensation.
- [ ] When should you *not* use event sourcing?
  - *Hint:* Simple CRUD domains, teams new to it, heavy reporting needs without read models, or when audit needs are met by simpler change logs.

**Day 71 — [Data architecture choices](sprints/sprint-09-mlops-document-pipeline.md#day-71)**

- [ ] Which database for mandates, chat history, documents, search and analytics?
  - *Hint:* SQL; Cosmos DB/document store; Blob; AI Search (+ vectors); lakehouse/warehouse via CDC. Justify each by access pattern.
- [ ] When do you use change data capture?
  - *Hint:* To feed search indexes, analytics or other services from the system of record without dual writes.
- [ ] A separate vector DB, or pgvector in your existing Postgres?
  - *Hint:* pgvector when scale is moderate and you value one system. A dedicated store/AI Search when you need hybrid search, scale or managed features.

**Day 79 — [Classic case studies: notifications and payments](sprints/sprint-10-model-and-prompt-lifecycle.md#day-79)**

- [ ] Design a notification system for 50 million users.
  - *Hint:* Ingest API → queue → preference/template service → per-channel workers → providers; dedupe; retries with backoff; DLQ; rate limits; analytics.
- [ ] Design a payment processing system.
  - *Hint:* Idempotent API, ledger as source of truth, state machine per payment, async PSP callbacks, reconciliation jobs, outbox for events, strong consistency where money moves.
- [ ] How do you guarantee a payment is never charged twice?
  - *Hint:* Idempotency keys end to end, a unique constraint on the payment ID, idempotent PSP calls, and reconciliation to catch the rest.

## Sprint scenarios (Build + Defend days)

**Day 8 — [Secure baseline, end to end](sprints/sprint-01-secure-baseline.md#day-8)**

- [ ] 20 application teams are moving to Azure. How do you structure subscriptions, identity and guardrails?
  - *Hint:* Cover management groups by archetype, subscription vending, Entra groups mapped to RBAC roles, PIM for admins, policy initiatives at management-group level, and a central connectivity hub.
- [ ] Explain Managed Identity vs service principal vs workload identity federation with a real example of each.
  - *Hint:* Managed Identity: Container App → Key Vault. Certificate-based service principal: an on-prem batch job. Federation: GitHub Actions → Azure.
- [ ] A connection string was committed to Git. What do you do now and later?
  - *Hint:* Now: rotate the secret immediately, assess access logs, then purge it from history. Later: push protection and secret scanning, Managed Identity instead of secrets, and pre-commit hooks.

**Day 16 — [Private internal AI assistant](sprints/sprint-02-private-ai-assistant.md#day-16)**

- [ ] The app can't reach Azure OpenAI over a private endpoint. Troubleshoot it.
  - *Hint:* DNS resolution from the caller, zone link, custom DNS forwarders, NSG/UDR, public access flag, identity and RBAC, then application logs. Show the commands you'd run.
- [ ] Front Door vs App Gateway vs API Management: where does each go?
  - *Hint:* Front Door: global edge. App Gateway: regional L7/WAF into the VNet. APIM: API product layer for auth, quotas, transformation and AI policies. They are often chained.
- [ ] How do you make LLM output reliable enough for downstream systems?
  - *Hint:* Schema-constrained output, validation, retries, fallbacks, tests in CI, and monitoring the parse-failure rate.

**Day 24 — [Policy-document Q&A, end to end](sprints/sprint-03-policy-document-qa.md#day-24)**

- [ ] Service Bus vs Event Grid vs Event Hubs: how did you use them here, and why?
  - *Hint:* Event Grid for the blob-created reaction, Service Bus for reliable processing with retries and DLQ. Event Hubs isn't needed at this volume.
- [ ] Someone changed a resource in the portal and Terraform now wants to destroy it. What do you do?
  - *Hint:* Read the plan, decide whether to codify or revert the change, and use `import`/`moved` where needed. Then fix the access that allowed it.
- [ ] How did you choose chunk size and overlap, and how would you prove it's right?
  - *Hint:* Structure-based chunking, then an evaluation set comparing 2–3 settings on hit rate and answer quality.

**Day 32 — [Permission-aware RAG, shipped by pipeline](sprints/sprint-04-permission-aware-rag.md#day-32)**

- [ ] HR documents must only be visible to HR. Show how your system enforces it.
  - *Hint:* Walk through ingestion ACLs, the query filter from token claims, negative tests, and ACL sync on group changes.
- [ ] RAG answers are wrong 20% of the time. How do you diagnose it?
  - *Hint:* Split retrieval and generation metrics, inspect failures by category, fix the biggest bucket first, and re-run evaluation in CI.
- [ ] Design CI/CD for 30 microservices and 6 teams.
  - *Hint:* Use your own pipeline as the worked example, then generalise with templates and governance.

**Day 40 — [Support-ticket agent on AKS](sprints/sprint-05-agent-on-aks.md#day-40)**

- [ ] A pod is in CrashLoopBackOff in production. What are your first five commands?
  - *Hint:* Demo it live on your cluster.
- [ ] Traffic spikes 10× at month-end. How do pods, nodes and the database each scale?
  - *Hint:* HPA/KEDA, cluster autoscaler with headroom, DB capacity (autoscale RU/vCore, read replicas, caching), plus a load test.
- [ ] When do you use an agent vs a fixed workflow, and what breaks agents in production?
  - *Hint:* Use your graph as the example: deterministic edges plus one agentic step. Failure modes: tool errors, loops, context growth, prompt injection through emails.

**Day 48 — [Game day: production readiness](sprints/sprint-06-production-readiness.md#day-48)**

- [ ] It's 2 a.m. and the AI assistant is slow. Walk me through your investigation.
  - *Hint:* Use your game-day evidence as the story.
- [ ] What SLOs would you set for an LLM-backed service, and why is latency hard there?
  - *Hint:* Your two SLOs plus quality SLIs; output-length variance and provider load.
- [ ] Design DR for a banking app with a 15-minute RPO.
  - *Hint:* Your DR doc.

**Day 56 — [Secure AI gateway](sprints/sprint-07-secure-ai-gateway.md#day-56)**

- [ ] A user tricks the assistant into revealing another customer's data. What failed, and how did you design against it?
  - *Hint:* Show identity-scoped retrieval, on-behalf-of, and your red-team results.
- [ ] The Azure OpenAI bill tripled this month. What do you check and change?
  - *Hint:* Show your gateway token dashboards.
- [ ] How do you secure the software supply chain from commit to cluster?
  - *Hint:* Walk through your pipeline and admission policies.

**Day 64 — [Same platform on AWS, plus MCP and GitOps](sprints/sprint-08-aws-mcp-gitops.md#day-64)**

- [ ] The company is going multi-cloud. What do you standardise and what do you leave cloud-native?
  - *Hint:* Standardise identity federation, IaC tooling, CI/CD, observability, security policies and containers. Keep managed data and AI services native per cloud.
- [ ] Migrate a 10-year-old on-prem .NET app to the cloud: which of the 6 Rs, and in what order?
  - *Hint:* Your migration drill.
- [ ] How do you let an LLM call internal systems safely?
  - *Hint:* Your MCP server and its security note.

**Day 72 — [Onboarding-document pipeline](sprints/sprint-09-mlops-document-pipeline.md#day-72)**

- [ ] A model works in the notebook and fails in production. List the likely causes.
  - *Hint:* Training/serving skew (different preprocessing), data drift, missing features at inference, environment or library differences, leakage in training, wrong threshold.
- [ ] How do you version data, code and model together so a prediction can be reproduced?
  - *Hint:* Your MLflow run, git SHA, data snapshot and environment, shown live.
- [ ] When would you fine-tune instead of using RAG?
  - *Hint:* Your ADR-008.

**Day 80 — [Model and prompt lifecycle](sprints/sprint-10-model-and-prompt-lifecycle.md#day-80)**

- [ ] How do you detect model degradation before you have labels?
  - *Hint:* Your drift dashboard.
- [ ] How do you test and release a prompt change safely?
  - *Hint:* Your CI gate, shown on a real PR.
- [ ] What does a platform team give app teams, and how do you know it's working?
  - *Hint:* Your template and its time-to-deploy number.

## Capstone

**Day 81 — [Scope, requirements and HLD](sprints/sprint-11-capstone.md#day-81)**

- [ ] Walk me through your system in 3 minutes.
  - *Hint:* Problem → users → architecture → the 3 hardest decisions → results (numbers).
- [ ] What were the key non-functional requirements and how did they shape the design?
  - *Hint:* Tie each NFR to a concrete choice (e.g. RPO 15 min → failover groups).
- [ ] What would you change with 10× users?
  - *Hint:* The scaling bottleneck, data partitioning, AI quota/PTU, cost.

**Day 82 — [LLD, ADRs, threat model and cost](sprints/sprint-11-capstone.md#day-82)**

- [ ] Which decision would you reverse, and why?
  - *Hint:* Pick a real one, explain what you learned.
- [ ] What is the biggest security risk in your system?
  - *Hint:* Name it, the control, and the residual risk.
- [ ] What does it cost per month and where would you cut first?
  - *Hint:* Numbers from your estimate.

**Day 83 — [.NET business services](sprints/sprint-11-capstone.md#day-83)**

- [ ] How do your services communicate, and why?
  - *Hint:* Sync for queries, async events for state changes; justify each.
- [ ] How do you keep data consistent across services?
  - *Hint:* Outbox, saga, idempotent consumers.
- [ ] How did you test the integration points?
  - *Hint:* Contract/integration tests, test containers, end-to-end smoke tests.

**Day 84 — [AI services integration](sprints/sprint-11-capstone.md#day-84)**

- [ ] How does a user's identity flow through the AI parts?
  - *Hint:* Token → gateway → on-behalf-of → MCP tools → API authorization.
- [ ] How do you know the assistant is good enough to launch?
  - *Hint:* Evaluation results, red-team results, guardrail coverage, a pilot with feedback.
- [ ] What happens when Azure OpenAI is down?
  - *Hint:* Gateway failover, degraded mode (search results without generation), clear user messaging.

**Day 85 — [Platform: Terraform, AKS, GitOps](sprints/sprint-11-capstone.md#day-85)**

- [ ] How long does it take to stand up a new environment, and what's manual?
  - *Hint:* Your real number. Aim for zero manual steps.
- [ ] How do you promote a change from dev to prod?
  - *Hint:* Same artifact, GitOps PR, approvals, canary.
- [ ] How do you handle infrastructure and app changes that depend on each other?
  - *Hint:* Ordering, feature flags, backward-compatible changes, expand/contract migrations.

**Day 86 — [Observability, dashboards and runbooks](sprints/sprint-11-capstone.md#day-86)**

- [ ] What are your SLOs and current error budget?
  - *Hint:* Real numbers from your dashboards.
- [ ] Walk me through your incident runbook for "AI assistant down".
  - *Hint:* Detection → triage → mitigation → communication → postmortem.
- [ ] How do you rotate a compromised secret with no downtime?
  - *Hint:* Two active versions, rolling update, managed identity where possible.

**Day 87 — [Hardening: security review, load test, rollback test](sprints/sprint-11-capstone.md#day-87)**

- [ ] What was the first bottleneck under load, and how did you fix it?
  - *Hint:* Real result from your test.
- [ ] Prove your rollback works.
  - *Hint:* Show the canary rollback evidence.
- [ ] What did your security review find?
  - *Hint:* Name findings and fixes; shows honesty and rigour.

**Day 88 — [Demo video and portfolio README](sprints/sprint-11-capstone.md#day-88)**

- [ ] Tell me about a project you're proud of.
  - *Hint:* Your capstone, in STAR form, with numbers.
- [ ] What would you do differently?
  - *Hint:* One honest technical and one process lesson.
- [ ] How would you take this to production in a real bank?
  - *Hint:* Governance, data protection, model risk management, change management, pilot, phased rollout.

## Interview-sprint rehearsal questions

**Day 89 — [Cloud scenario rehearsal](sprints/sprint-12-interview-sprint.md#day-89)**

- [ ] Design the network and identity for a regulated workload on Azure.
  - *Hint:* Hub-spoke, private endpoints, Entra + PIM, policy guardrails, logging.
- [ ] An app can't reach a PaaS service after a private endpoint was added. Troubleshoot it.
  - *Hint:* DNS → zone link → forwarders → NSG/UDR → public access → RBAC.
- [ ] Design DR for a banking app with a 15-minute RPO.
  - *Hint:* Your DR doc.

**Day 90 — [AI engineering scenario rehearsal](sprints/sprint-12-interview-sprint.md#day-90)**

- [ ] Design an enterprise RAG assistant for 10,000 employees with document-level permissions.
  - *Hint:* Ingestion, chunking, hybrid search, ACL filtering, gateway, guardrails, evaluation, monitoring.
- [ ] Your RAG is wrong 20% of the time. Fix it.
  - *Hint:* Separate retrieval vs generation, measure, fix the biggest bucket.
- [ ] How do you secure an agent that can take actions?
  - *Hint:* Least-privilege tools, user identity, approvals, injection defences, audit.

**Day 91 — [DevOps and platform rehearsal + live troubleshooting](sprints/sprint-12-interview-sprint.md#day-91)**

- [ ] Design CI/CD for 30 microservices owned by 6 teams.
  - *Hint:* Templates, build once, scan/sign, GitOps, approvals, DORA.
- [ ] A pod is in CrashLoopBackOff in production. Go.
  - *Hint:* The commands, in order, narrated.
- [ ] How do you structure Terraform for many teams and environments?
  - *Hint:* Modules, state separation, PR plans, policy.

**Day 92 — [System design rounds (timed)](sprints/sprint-12-interview-sprint.md#day-92)**

- [ ] Design a WhatsApp-like messaging system.
  - *Hint:* Connections (WebSockets), message store, fan-out, delivery receipts, offline delivery, ordering per chat, scale numbers.
- [ ] Design an Uber-like ride-matching system.
  - *Hint:* Location updates, geo-indexing, matching service, surge, consistency of trip state.
- [ ] Design a distributed job scheduler.
  - *Hint:* Job store, leader election/locking, at-least-once execution, idempotent jobs, retries, monitoring.

**Day 93 — [STAR stories, CV and profiles](sprints/sprint-12-interview-sprint.md#day-93)**

- [ ] Tell me about yourself.
  - *Hint:* 90 seconds: background → what you've built recently → what you want next.
- [ ] Why are you moving towards cloud/AI/platform work?
  - *Hint:* A genuine reason backed by what you built.
- [ ] Tell me about a time you failed.
  - *Hint:* A real failure, what you changed, the result.

## Mock interview questions

**Day 94 — [Cloud and architecture (whiteboard)](sprints/sprint-12-interview-sprint.md#day-94)**

- [ ] Design an Azure platform for a bank's internal AI assistant used by 10,000 staff.
  - *Hint:* Full design using your capstone.
- [ ] Private endpoint resolution failed in production. What happened?
  - *Hint:* DNS troubleshooting path.
- [ ] The region is down. What happens to your system?
  - *Hint:* DR walkthrough with RTO/RPO.

**Day 95 — [AI engineering (design + live build/debug)](sprints/sprint-12-interview-sprint.md#day-95)**

- [ ] Design an AI agent for onboarding documents with approvals.
  - *Hint:* Document pipeline + agent + human-in-the-loop + audit.
- [ ] An uploaded document contains hidden instructions. What does your system do?
  - *Hint:* Indirect injection defences.
- [ ] How do you decide this is ready to launch?
  - *Hint:* Evaluation gates, red-team, pilot, monitoring.

**Day 96 — [DevOps/platform + behavioural, then final review](sprints/sprint-12-interview-sprint.md#day-96)**

- [ ] Design the delivery platform for 30 microservices across 6 teams.
  - *Hint:* Your pipeline + GitOps + templates + policy.
- [ ] Production is down after a deploy. Walk me through the first 15 minutes.
  - *Hint:* Incident handling + rollback.
- [ ] Why should we hire you?
  - *Hint:* .NET depth + cloud/AI/platform builds + architecture judgement, with proof.

