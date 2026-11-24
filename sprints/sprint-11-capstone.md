# Sprint 11 — Capstone: Enterprise AI banking platform (Days 81–88)

**Scenario you build:** one coherent platform covering corporate onboarding, mandate management, document processing, notifications and an AI support assistant. Use synthetic data only, never employer code or real customer data.

Almost every part exists from Sprints 1–10. The new work is making it one system and documenting it like an architect.

[← Back to tracker](../TRACKER.md)

---

<a id="day-81"></a>
### Day 81 · Capstone · Scope, requirements and HLD

**Time:** ~3 h

**Why it matters:** the capstone is your main interview story, and it starts with clear requirements.

**Learn**
- How to write functional vs non-functional requirements an architect would sign off.
- C4 model: context and container diagrams.

**Do**
- [ ] One-page scope: users, journeys (onboard company → submit mandate → approve → notify; ask the assistant)
- [ ] Non-functionals: availability, latency, RPO/RTO, data residency, compliance, cost ceiling
- [ ] HLD: C4 context + container diagrams in `docs/architecture/`

**Interview questions**
1. **Walk me through your system in 3 minutes.** — Problem → users → architecture → the 3 hardest decisions → results (numbers).
2. **What were the key non-functional requirements and how did they shape the design?** — Tie each NFR to a concrete choice (e.g. RPO 15 min → failover groups).
3. **What would you change with 10× users?** — The scaling bottleneck, data partitioning, AI quota/PTU, cost.

**Gotchas**
- A scope so big it never finishes. Cut to the journeys you can demo.

**Done when:** a non-technical person understands the context diagram.

**Resources:** [C4 model](https://c4model.com/) · [Azure Architecture Center](https://learn.microsoft.com/azure/architecture/)

---

<a id="day-82"></a>
### Day 82 · Capstone · LLD, ADRs, threat model and cost

**Time:** ~3 h

**Why it matters:** this is the documentation set that makes you look like an architect, not just a coder.

**Do**
- [ ] LLD for 2 services: component and sequence diagrams, API contracts (OpenAPI), data model
- [ ] Consolidate 8–10 ADRs from earlier sprints into `docs/adr/` with an index
- [ ] STRIDE threat model updated for the full system
- [ ] Monthly cost estimate (Azure Pricing Calculator) with the top cost drivers

**Interview questions**
1. **Which decision would you reverse, and why?** — Pick a real one, explain what you learned.
2. **What is the biggest security risk in your system?** — Name it, the control, and the residual risk.
3. **What does it cost per month and where would you cut first?** — Numbers from your estimate.

**Gotchas**
- ADRs written after the fact without the options you rejected. Always record alternatives.

**Done when:** every major component in the HLD links to an ADR or LLD.

**Resources:** [ADR templates](https://adr.github.io/) · [Microsoft Threat Modeling Tool](https://learn.microsoft.com/azure/security/develop/threat-modeling-tool)

---

<a id="day-83"></a>
### Day 83 · Capstone · .NET business services

**Time:** ~3 h

**Do**
- [ ] Onboarding, mandate and notification services in .NET 8 (extend Sprint 1–4 work)
- [ ] Outbox + Service Bus events; saga for approval; Entra auth with app roles
- [ ] Unit + integration tests (Testcontainers for SQL/Service Bus emulator if possible)

**Interview questions**
1. **How do your services communicate, and why?** — Sync for queries, async events for state changes; justify each.
2. **How do you keep data consistent across services?** — Outbox, saga, idempotent consumers.
3. **How did you test the integration points?** — Contract/integration tests, test containers, end-to-end smoke tests.

**Gotchas**
- Gold-plating the .NET side. It's your strongest area; keep the time balanced.

**Done when:** an onboarding flow runs end to end via the APIs.

**Resources:** [.NET microservices guide](https://learn.microsoft.com/dotnet/architecture/microservices/) · [Testcontainers for .NET](https://dotnet.testcontainers.org/)

---

<a id="day-84"></a>
### Day 84 · Capstone · AI services integration

**Time:** ~3 h

**Do**
- [ ] Permission-aware RAG assistant through the APIM AI gateway
- [ ] Document pipeline (extraction → review → risk model) wired into onboarding
- [ ] Approval agent using MCP tools with the user's identity
- [ ] Guardrails and tracing on every AI call

**Interview questions**
1. **How does a user's identity flow through the AI parts?** — Token → gateway → on-behalf-of → MCP tools → API authorization.
2. **How do you know the assistant is good enough to launch?** — Evaluation results, red-team results, guardrail coverage, a pilot with feedback.
3. **What happens when Azure OpenAI is down?** — Gateway failover, degraded mode (search results without generation), clear user messaging.

**Gotchas**
- Integration is where auth breaks. Test with two users with different roles.

**Done when:** two users with different roles get correctly different answers and actions.

**Resources:** [Baseline Microsoft Foundry chat reference architecture](https://learn.microsoft.com/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat)

---

<a id="day-85"></a>
### Day 85 · Capstone · Platform: Terraform, AKS, GitOps

**Time:** ~3 h

**Do**
- [ ] One `terraform apply` per environment creates network, AKS, data, AI, APIM, monitoring
- [ ] Argo CD deploys all services; canary on the AI service
- [ ] Pipelines: CI with scans/signing → GitOps promotion

**Interview questions**
1. **How long does it take to stand up a new environment, and what's manual?** — Your real number. Aim for zero manual steps.
2. **How do you promote a change from dev to prod?** — Same artifact, GitOps PR, approvals, canary.
3. **How do you handle infrastructure and app changes that depend on each other?** — Ordering, feature flags, backward-compatible changes, expand/contract migrations.

**Gotchas**
- Hidden manual steps (DNS records, role assignments). Find them by rebuilding from scratch.

**Done when:** `destroy` + `apply` + GitOps sync rebuilds a working environment.

**Resources:** [AKS baseline architecture](https://learn.microsoft.com/azure/architecture/reference-architectures/containers/aks/baseline-aks)

---

<a id="day-86"></a>
### Day 86 · Capstone · Observability, dashboards and runbooks

**Time:** ~3 h

**Do**
- [ ] Dashboards: user journeys (SLOs), platform health, LLM cost/latency/quality, model drift
- [ ] Alerts with burn-rate rules; on-call runbooks for the top 5 failure modes
- [ ] Runbooks: deployment, rollback, incident response, key rotation, DR failover

**Interview questions**
1. **What are your SLOs and current error budget?** — Real numbers from your dashboards.
2. **Walk me through your incident runbook for "AI assistant down".** — Detection → triage → mitigation → communication → postmortem.
3. **How do you rotate a compromised secret with no downtime?** — Two active versions, rolling update, managed identity where possible.

**Gotchas**
- Dashboards nobody would actually look at during an incident. Design them for the runbooks.

**Done when:** every alert links to a runbook.

**Resources:** [Google SRE book](https://sre.google/sre-book/table-of-contents/)

---

<a id="day-87"></a>
### Day 87 · Capstone · Hardening: security review, load test, rollback test

**Time:** ~3 h

**Do**
- [ ] Security checklist: Defender recommendations, no public endpoints except the gateway, local auth off, policies enforced, red-team re-run
- [ ] Load test one journey (Azure Load Testing, k6 or Locust); record limits and the first bottleneck
- [ ] Deliberately bad release: confirm the canary rolls back; confirm the DB migration is backward compatible

**Interview questions**
1. **What was the first bottleneck under load, and how did you fix it?** — Real result from your test.
2. **Prove your rollback works.** — Show the canary rollback evidence.
3. **What did your security review find?** — Name findings and fixes; shows honesty and rigour.

**Gotchas**
- Load testing against shared AI quotas can lock you out. Use a separate deployment or mock the LLM.

**Done when:** you have load-test numbers and rollback evidence in the README.

**Resources:** [k6 docs](https://grafana.com/docs/k6/latest/) · [Azure Load Testing](https://learn.microsoft.com/azure/load-testing/)

---

<a id="day-88"></a>
### Day 88 · Capstone · Demo video and portfolio README

**Time:** ~3 h

**Do**
- [ ] README a hiring manager can read in 3 minutes: problem, architecture diagram, what it shows, key numbers, links to ADRs
- [ ] 5-minute demo video: user journey → AI features → platform (GitOps, dashboards) → one failure and recovery
- [ ] Pin the repo on your GitHub profile; add a short write-up on LinkedIn

**Interview questions**
1. **Tell me about a project you're proud of.** — Your capstone, in STAR form, with numbers.
2. **What would you do differently?** — One honest technical and one process lesson.
3. **How would you take this to production in a real bank?** — Governance, data protection, model risk management, change management, pilot, phased rollout.

**Gotchas**
- A README that lists technologies instead of outcomes and decisions.

**Done when:** a friend watches the video and can explain what you built.

**Resources:** [GitHub profile README docs](https://docs.github.com/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme)
