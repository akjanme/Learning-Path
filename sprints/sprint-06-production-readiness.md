# Sprint 6 — Production readiness (Days 41–48)

**Scenario you build:** full observability (logs, metrics, traces, LLM cost), SLOs with burn-rate alerts, a DR design, and a game day where you break things on purpose and diagnose them from telemetry alone.

[← Back to tracker](../TRACKER.md)

---

<a id="day-41"></a>
### Day 41 · Cloud · Azure Monitor, Log Analytics, KQL, Application Insights

**Time:** ~3 h

**Why it matters:** every incident and troubleshooting question assumes you can find the evidence quickly.

**Learn**
- **Signals:** metrics vs logs vs traces, and when each is cheapest and most useful.
- **Log Analytics:** workspace design (central vs per-app), diagnostic settings, retention and table plans (Analytics vs Basic logs) for cost.
- **Application Insights:** workspace-based, distributed tracing, dependency tracking, availability tests, custom metrics.
- **KQL:** `where`, `summarize`, `bin`, `join`, `percentile`, `render`.
- **Alerts:** metric vs log alerts, action groups, Container Insights for AKS.

**Do**
- [ ] Diagnostic settings for all resources, via Terraform or an Azure Policy (DeployIfNotExists)
- [ ] Save 5 KQL queries in `observability/kql/`: errors by operation, p95 latency, failed dependencies, token usage per request, pod restarts
- [ ] One log alert routed to an action group (email)

**Interview questions**
1. **What do you monitor for an API?** — The RED metrics (rate, errors, duration) per endpoint, dependency health, saturation (CPU, memory, connection pools), business KPIs, and synthetic availability checks.
2. **How do you cut Log Analytics cost?** — Drop noisy logs at the source, set log levels, use Basic/auxiliary plans for verbose tables, sampling, shorter retention, and data collection rules.
3. **How do you trace one request across services?** — W3C trace context propagated through HTTP and messages, with a correlated operation ID in App Insights/OpenTelemetry.

**Gotchas**
- Verbose debug logging in production makes ingestion cost explode.
- Aggressive sampling can hide rare errors. Keep all failures.
- Alerting on causes (CPU) instead of symptoms (errors, latency) creates noise.

**Scenario:** the monthly Azure bill shows Log Analytics as your #2 cost. Fix it without losing incident visibility.

**Done when:** you can find the slowest dependency of any request in under 2 minutes.

**Resources:** [KQL overview](https://learn.microsoft.com/kusto/query/) · [Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)

---

<a id="day-42"></a>
### Day 42 · Cloud · High availability and disaster recovery

**Time:** ~3 h

**Why it matters:** banks and regulated firms ask for RTO/RPO-driven designs, and "untested DR" is a red flag.

**Learn**
- **Terms:** availability zones vs regions; composite SLAs; RTO vs RPO.
- **DR patterns:** backup/restore → pilot light → warm standby → active-active, with their cost and complexity.
- **Data:** SQL failover groups, Cosmos DB multi-region writes/reads, geo-redundant storage, asynchronous replication = your RPO.
- **Traffic:** Front Door / Traffic Manager failover; DNS TTL.
- **AI-specific:** Azure OpenAI capacity and model availability in the DR region.

**Do**
- [ ] Write `docs/dr-design.md` for the banking app: RTO 1 h, RPO 15 min, which pattern, cost estimate
- [ ] Make your services zone-redundant where supported
- [ ] Run (or simulate on paper, step by step) a SQL failover-group failover

**Interview questions**
1. **Design DR for a banking app with a 15-minute RPO.** — Zone-redundant primary; async geo-replication for data (SQL failover group, Cosmos multi-region); IaC to rebuild compute in the secondary; Front Door failover; tested runbooks; quarterly drills.
2. **Calculate a composite SLA.** — Serial dependencies multiply: 99.95% × 99.99% ≈ 99.94%. Redundancy improves it; show the maths.
3. **What are the pitfalls of active-active?** — Write conflicts, data consistency, double cost, complex testing, and hidden single points (one DNS, one identity provider).

**Gotchas**
- Assuming the paired region has capacity, or the same AI models, when you need them.
- DNS TTLs and client caching delay failover.
- A DR plan that was never tested isn't a DR plan.

**Scenario:** West Europe is down. Walk through the first 30 minutes, minute by minute.

**Done when:** your DR doc names each RTO/RPO, the mechanism behind it, and how you test it.

**Resources:** [Azure reliability docs](https://learn.microsoft.com/azure/reliability/) · [Well-Architected reliability pillar](https://learn.microsoft.com/azure/well-architected/reliability/)

---

<a id="day-43"></a>
### Day 43 · AI · LLM tracing, token cost and latency

**Time:** ~3 h

**Why it matters:** LLMOps interviews always ask "how do you know what your AI system is doing and costing?"

**Learn**
- **Spans:** separate spans for retrieval, reranking, LLM calls and tool calls; the OpenTelemetry GenAI semantic conventions.
- **Tools:** LangSmith, Microsoft Foundry (formerly Azure AI Foundry) tracing, App Insights.
- **Cost:** tokens × price per call, aggregated per user, tenant or feature; embedding costs too.
- **Latency breakdown:** time to first token, tokens/second, retrieval time, tool time.
- **Privacy:** what you may log (prompts and responses can contain PII).

**Do**
- [ ] Instrument the RAG API and agent with OpenTelemetry (or LangSmith)
- [ ] Dashboard: cost per request, p95 latency per step, tokens per feature
- [ ] Find and fix the slowest step

**Interview questions**
1. **The AI assistant is slow. How do you find where the time goes?** — Look at the trace waterfall: retrieval vs LLM (time to first token, output length) vs tools. Fix the biggest contributor first.
2. **How do you track LLM cost per tenant?** — Tag every call with tenant/feature, record usage tokens, multiply by price in the pipeline or dashboard, and set budgets and alerts.
3. **Should you log prompts and responses?** — Only with a policy: redact PII, separate secure store, retention limits, access controls. Log metadata by default.

**Gotchas**
- Full prompts in shared logs is a compliance incident.
- High-cardinality metric labels (user IDs) blow up the metrics backend.
- Forgetting embedding and reranker costs.

**Scenario:** finance asks which feature drives 70% of the AI spend. Answer with data.

**Done when:** your dashboard shows cost and latency per step for the last 100 requests.

**Resources:** [OpenTelemetry GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) · [LangSmith docs](https://docs.smith.langchain.com/)

---

<a id="day-44"></a>
### Day 44 · AI · Latency optimisation and prompt management

**Time:** ~3 h

**Why it matters:** production AI work is mostly making things faster, cheaper and safely changeable.

**Learn**
- **Latency levers:** streaming (SSE), smaller models for routing and classification, parallel tool calls, shorter prompts, `max_tokens`, prompt caching, semantic caching.
- **Prompt management:** prompts in version control, IDs and versions logged on every trace, A/B or shadow testing.
- **Capacity models:** pay-as-you-go vs provisioned throughput (PTU); global vs data-zone vs regional deployments, and the data-residency implications.

**Do**
- [ ] Stream responses from FastAPI to the client
- [ ] Router: a small model classifies intent, and only complex questions go to the large model
- [ ] Prompt templates in `prompts/` with a version, logged on each trace

**Interview questions**
1. **How would you cut AI response latency by 50%?** — Stream, route simple requests to small models, trim context, cache, parallelise retrieval and tools, and cap output length. Measure time to first token separately.
2. **How do you release a prompt change safely?** — Version it, run the eval suite in CI, shadow or A/B test on a slice of traffic, monitor quality metrics, and keep instant rollback to the previous version.
3. **PTU or pay-as-you-go?** — PTU for steady, high, latency-sensitive load (predictable performance and cost). Pay-as-you-go for spiky or early-stage workloads, often with spillover between them.

**Gotchas**
- Streaming breaks behind proxies that buffer responses (check App Gateway/APIM settings).
- A cache that ignores user context or permissions.
- Global deployments may process data outside your region, so check data residency rules.

**Scenario:** the business wants answers in under 2 seconds and costs halved. What do you trade?

**Done when:** you can show before/after latency and cost numbers for the router change.

**Resources:** [Azure OpenAI deployment types](https://learn.microsoft.com/azure/ai-services/openai/how-to/deployment-types) · [Latency optimization guide](https://platform.openai.com/docs/guides/latency-optimization)

---

<a id="day-45"></a>
### Day 45 · DevOps · Prometheus, Grafana and OpenTelemetry on Kubernetes

**Time:** ~3 h

**Why it matters:** Prometheus/Grafana is the industry-standard metrics stack, and on-call roles expect PromQL basics.

**Learn**
- **Prometheus:** pull model, exporters, ServiceMonitors, recording rules.
- **PromQL basics:** `rate()`, `sum by`, `histogram_quantile()`.
- **Grafana:** dashboards and alerting.
- **OpenTelemetry Collector:** receivers → processors → exporters.
- **Managed options:** Azure Managed Prometheus and Managed Grafana.
- **Methods:** RED for services, USE for resources.

**Do**
- [ ] Install kube-prometheus-stack on `kind` (or enable Managed Prometheus on AKS)
- [ ] Expose metrics from .NET and Python apps
- [ ] Build a RED dashboard per service; add an OpenTelemetry collector exporting traces

**Interview questions**
1. **RED vs USE?** — RED (rate, errors, duration) for request-driven services. USE (utilisation, saturation, errors) for resources such as CPU, disk and pools.
2. **How do you compute p95 latency in Prometheus?** — `histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))`.
3. **Metrics vs logs vs traces: when do you use each?** — Metrics for alerting and trends (cheap). Traces for where time goes. Logs for detailed context on specific events.

**Gotchas**
- `rate()` on a gauge (it's for counters).
- High-cardinality labels (user IDs, URLs with IDs) overload Prometheus.
- Averages hide tail latency. Use percentiles.

**Scenario:** p50 latency looks fine but users complain. What's happening, and which panel shows it?

**Done when:** your dashboard shows rate, errors and p95 for every service.

**Resources:** [Prometheus docs](https://prometheus.io/docs/) · [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)

---

<a id="day-46"></a>
### Day 46 · DevOps · SLOs, alerting and incident response

**Time:** ~3 h

**Why it matters:** how you run incidents and set reliability targets separates senior engineers from tool operators.

**Learn**
- **Definitions:** SLI vs SLO vs SLA; error budgets.
- **Alerting:** multi-window burn-rate alerts; page on user pain, ticket on the rest.
- **Incident roles:** incident commander, communications, operations; severity levels.
- **Learning:** runbooks, blameless postmortems, action-item follow-through.

**Do**
- [ ] Define 2 SLOs (availability 99.9%, p95 latency < 3 s for `/ask`)
- [ ] Burn-rate alert for the availability SLO
- [ ] Runbook: "AI assistant slow or failing"

**Interview questions**
1. **What SLOs would you set for an LLM-backed service?** — Availability, p95 time to first token, end-to-end latency, plus quality SLIs such as groundedness rate and refusal rate. Explain why LLM latency varies (output length, provider load).
2. **It's 2 a.m. and the assistant is slow. Walk me through it.** — Acknowledge and assess impact; check dashboards and recent changes; trace a slow request; mitigate first (roll back, fail over, route to a smaller model); communicate; postmortem.
3. **What makes a good postmortem?** — Blameless, a timeline, root cause *and* contributing factors, what went well, owned and dated action items.

**Gotchas**
- 100% targets leave no room to ship changes.
- Paging on CPU spikes that don't affect users.
- Postmortems that blame a person.

**Scenario:** you've burned 80% of the month's error budget in week 1. What do you do?

**Done when:** your SLO alert fires correctly in a test.

**Resources:** [Google SRE book (free)](https://sre.google/sre-book/table-of-contents/) · [Google SRE workbook: alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)

---

<a id="day-47"></a>
### Day 47 · .NET + Design · Observability design in .NET

**Time:** ~2 h

**Why it matters:** architects are asked how to make 30 services debuggable, and .NET has strong OpenTelemetry support.

**Learn**
- **OpenTelemetry .NET:** tracing (`ActivitySource`), metrics (`Meter`), logs; OTLP and Azure Monitor exporters.
- **Context propagation:** W3C `traceparent` over HTTP *and* in Service Bus message properties.
- **Structured logging:** `ILogger` with message templates, scopes, correlation IDs.
- **Health checks:** liveness vs readiness endpoints in ASP.NET Core.

**Do**
- [ ] Add OpenTelemetry to the .NET API (exporting to App Insights or OTLP)
- [ ] Propagate trace context through Service Bus messages
- [ ] Separate `/health/live` and `/health/ready` endpoints

**Interview questions**
1. **How do you trace across asynchronous messaging?** — Inject trace context into message properties on publish and extract it on consume, creating linked spans.
2. **How do you design observability for 30 services?** — Standard telemetry library/template, OpenTelemetry everywhere, central backends, naming conventions, golden dashboards per service, SLOs per user journey.
3. **When do you use logs vs traces?** — Traces for flow and timing across services; logs for detailed events, correlated by trace ID.

**Gotchas**
- Trace context is lost over queues unless propagated explicitly.
- Debug log level left on in production.
- Different sampling decisions per service break traces.

**Scenario:** a payment is "stuck" somewhere between 4 services and a queue. How do you find where?

**Done when:** one trace shows HTTP → .NET → Service Bus → worker end to end.

**Resources:** [.NET observability with OpenTelemetry](https://learn.microsoft.com/dotnet/core/diagnostics/observability-with-otel) · [Health checks in ASP.NET Core](https://learn.microsoft.com/aspnet/core/host-and-deploy/health-checks)

---

<a id="day-48"></a>
### Day 48 · Build + Defend · Game day: production readiness

**Time:** ~4 h

**Do**
- [ ] Break three things on purpose: (1) a bad config value, (2) an expired or removed secret, (3) a node failure (cordon and drain, or delete a node)
- [ ] Diagnose each *only* from dashboards, traces and logs; time yourself
- [ ] Write a postmortem for each in `docs/postmortems/`
- [ ] Add the DR design and SLOs to the README
- [ ] Record answers to the three questions below

**Interview questions**
1. **It's 2 a.m. and the AI assistant is slow. Walk me through your investigation.** — Use your game-day evidence as the story.
2. **What SLOs would you set for an LLM-backed service, and why is latency hard there?** — Your two SLOs plus quality SLIs; output-length variance and provider load.
3. **Design DR for a banking app with a 15-minute RPO.** — Your DR doc.

**Gotchas**
- Game days that only test what you know will work. Include one failure you haven't seen before.

**Done when:** all three induced failures were found from telemetry in under 15 minutes each.
