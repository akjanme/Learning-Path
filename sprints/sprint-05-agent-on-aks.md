# Sprint 5 — Support-ticket agent on AKS (Days 33–40)

**Scenario you build:** a LangGraph agent reads a customer email, looks up the account through the .NET API, drafts a ticket and waits for human approval before creating it. Everything runs on AKS with workload identity, Helm and autoscaling.

[← Back to tracker](../TRACKER.md)

---

<a id="day-33"></a>
### Day 33 · Cloud · AKS architecture: node pools, networking, upgrades

**Time:** ~3 h

**Why it matters:** AKS is the default enterprise container platform on Azure, and design and upgrade questions are standard.

**Learn**
- **Control plane vs nodes:** the managed control plane; system vs user node pools; VM sizes; availability zones.
- **Networking models:** Azure CNI Overlay (recommended default), Azure CNI with pod subnet, CNI powered by Cilium. kubenet is being retired.
- **Upgrades:** control plane first, then node pools with max surge; PodDisruptionBudgets; auto-upgrade and node OS upgrade channels; maintenance windows.
- **Cluster types:** private clusters and API server access; AKS Automatic (awareness).

**Do**
- [ ] AKS via Terraform: CNI Overlay, system pool + user pool across 3 zones, cluster autoscaler enabled
- [ ] Add a PDB to a test deployment, then upgrade the user pool with max surge and watch it drain

**Interview questions**
1. **Why separate system and user node pools?** — To isolate critical system pods (CoreDNS, metrics) from app workloads and scale or size pools independently. Taint the system pool.
2. **Which AKS networking model and why?** — Usually CNI Overlay: pods get IPs from an overlay range, saving VNet IPs, with good performance. Choose a VNet-routable pod IP only when external systems must reach pods directly.
3. **How do you do zero-downtime AKS upgrades?** — PDBs, multiple replicas spread across zones, max surge, readiness probes, maintenance windows, and upgrading a non-prod cluster first.

**Gotchas**
- No PDBs means an upgrade can evict all replicas at once.
- Classic Azure CNI exhausts subnet IPs (one IP per pod).
- Running app workloads on the system pool.
- Each Kubernetes minor version is supported for roughly a year. Falling behind forces rushed multi-version upgrades.

**Scenario:** an AKS upgrade caused a 10-minute outage. Write the postmortem's root cause and fixes.

**Done when:** a node pool upgrade completes while a test app keeps serving traffic.

**Resources:** [AKS docs](https://learn.microsoft.com/azure/aks/) · [AKS baseline architecture](https://learn.microsoft.com/azure/architecture/reference-architectures/containers/aks/baseline-aks)

---

<a id="day-34"></a>
### Day 34 · Cloud · AKS identity, ingress and autoscaling

**Time:** ~3 h

**Why it matters:** "pods accessing Azure without secrets" and "scaling under spikes" are the two most common AKS interview scenarios.

**Learn**
- **Workload Identity:** cluster OIDC issuer + federated credential + annotated service account; the pod label `azure.workload.identity/use: "true"`.
- **Secrets:** the Key Vault Secrets Store CSI driver.
- **Ingress options:** the App Routing add-on, Application Gateway for Containers, Gateway API. The community ingress-nginx project has been retired, so check current AKS guidance.
- **Autoscaling:** HPA (needs resource requests), KEDA (event-driven, e.g. queue length), cluster autoscaler or node auto-provisioning.

**Do**
- [ ] Give the RAG API workload identity to AI Search and Azure OpenAI (no keys)
- [ ] Mount one Key Vault secret via the CSI driver
- [ ] Ingress with TLS
- [ ] HPA on CPU for the API; KEDA on Service Bus queue length for the worker

**Interview questions**
1. **How does a pod access Azure resources without secrets?** — Workload identity: Kubernetes issues a service-account token, Entra trusts the cluster's OIDC issuer via a federated credential, and the SDK exchanges the token for an Entra token.
2. **HPA vs KEDA vs cluster autoscaler?** — HPA scales pods on metrics. KEDA scales pods on events (queues, streams), including to zero. The cluster autoscaler adds or removes nodes when pods can't be scheduled.
3. **Traffic spikes 10× at month-end. What scales, and how fast?** — Pods scale in seconds, nodes in minutes, so you need headroom or overprovisioning. Pre-scale for known peaks, and check database and downstream limits.

**Gotchas**
- A missing workload-identity label or service-account annotation gives auth errors that look like RBAC problems.
- HPA can't compute CPU utilisation without resource requests.
- Node provisioning lag: pods sit Pending during spikes.

**Scenario:** the worker can't keep up with the queue at 9 a.m. every day. Design the scaling.

**Done when:** loading the queue scales the worker up, and an empty queue scales it back down.

**Resources:** [AKS workload identity](https://learn.microsoft.com/azure/aks/workload-identity-overview) · [KEDA docs](https://keda.sh/docs/)

---

<a id="day-35"></a>
### Day 35 · AI · Tool calling and the agent loop, from scratch

**Time:** ~3 h

**Why it matters:** if you understand the agent loop without a framework, you can debug any framework.

**Learn**
- **The loop:** the model reasons → picks a tool → your code executes it → the result goes back → repeat until done or a limit.
- **Stop conditions:** max iterations, token/time budget, explicit "final answer".
- **Tool design:** narrow, typed, idempotent, with clear descriptions and permission checks inside the tool.
- **Agent vs workflow:** prefer deterministic workflows; use agents where the path genuinely varies.
- **Memory:** short-term (conversation) vs long-term (stored facts).

**Do**
- [ ] Plain-Python agent (no framework) with 3 tools against the .NET API: `get_customer`, `get_open_tickets`, `draft_ticket`
- [ ] Log every step (thought, tool, arguments, result, tokens)
- [ ] Cap iterations and handle tool errors gracefully

**Interview questions**
1. **When do you use an agent, and when a fixed workflow?** — A workflow when the steps are known: cheaper, testable, predictable. An agent when the steps depend on the input and can't be enumerated. Many good systems are workflows with small agentic steps.
2. **How do you stop runaway loops and cost?** — Iteration and token budgets, timeouts, loop detection, and fallback to a human.
3. **How do you control what tools an agent can do?** — Least-privilege tools, authorization with the user's identity inside each tool, and confirmation for side-effecting actions.

**Gotchas**
- Too many tools confuse the model.
- Side-effecting tools without confirmation.
- Non-idempotent tools that get retried.

**Scenario:** the agent created 14 duplicate tickets overnight. Find the cause and prevent it.

**Done when:** you can show a full step-by-step trace of one agent run.

**Resources:** [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · [OpenAI function calling guide](https://platform.openai.com/docs/guides/function-calling)

---

<a id="day-36"></a>
### Day 36 · AI · LangGraph: stateful agents with human approval

**Time:** ~3 h

**Why it matters:** real enterprise agents need durable state, approvals and resumability. LangGraph is widely used for this.

**Learn**
- **Graph model:** `StateGraph`, nodes, edges, conditional edges, state reducers.
- **Persistence:** checkpointers (Postgres) for resuming and auditing.
- **Human-in-the-loop:** interrupts that pause for approval and resume later.
- **Streaming:** steps and tokens.
- **Alternatives:** Microsoft Foundry Agent Service, Semantic Kernel / Microsoft Agent Framework, AutoGen (awareness).

**Do**
- [ ] Graph: classify email → look up account → draft ticket → **interrupt for approval** → create ticket
- [ ] Postgres checkpointer; resume a paused run from a separate process
- [ ] Unit tests for each node

**Interview questions**
1. **Why model an agent as a graph?** — Explicit control flow, inspectable state, deterministic edges where possible, and easy insertion of approvals and retries.
2. **How does an approval that happens two days later resume the run?** — Persisted state in a checkpointer keyed by thread ID. The approval event resumes the graph from the interrupt.
3. **How do you test agents?** — Unit-test nodes with mocked LLMs and tools, use scenario tests on recorded cases, run evaluations on trajectories, and keep end-to-end tests few but realistic.

**Gotchas**
- Message history grows without limit and blows up context and cost. Summarise or trim it.
- An in-memory checkpointer in production loses every paused run on restart.
- Non-deterministic paths make end-to-end tests flaky, so test nodes in isolation.

**Scenario:** compliance asks who approved ticket #4471 and what the agent saw at the time. Can you answer?

**Done when:** a run pauses, survives a restart and resumes after approval.

**Resources:** [LangChain Academy (LangGraph)](https://academy.langchain.com/) · [LangGraph docs](https://langchain-ai.github.io/langgraph/)

---

<a id="day-37"></a>
### Day 37 · DevOps · Kubernetes core objects

**Time:** ~3 h

**Why it matters:** you can't operate AKS, or pass a platform interview, without these fundamentals.

**Learn**
- **Workloads:** Pods, ReplicaSets, Deployments (rolling update `maxSurge`/`maxUnavailable`), namespaces, labels and selectors.
- **Services:** ClusterIP, NodePort, LoadBalancer; endpoints.
- **Config:** ConfigMaps and Secrets (base64 is not encryption).
- **Probes:** liveness, readiness, startup, and what each one is for.
- **Resources:** requests vs limits, QoS classes, OOMKilled, CPU throttling.

**Do**
- [ ] Local cluster with `kind` or `k3d`
- [ ] Deploy the API with probes and resources
- [ ] Break readiness and watch traffic stop going to that pod
- [ ] Set a tiny memory limit and observe OOMKilled

**Interview questions**
1. **Liveness vs readiness vs startup probes?** — Readiness: can it take traffic (removed from the Service if not). Liveness: is it stuck (restart it). Startup: protects slow starters from liveness kills.
2. **Requests vs limits?** — Requests are used for scheduling and guaranteed capacity. Limits cap usage: memory over the limit gets OOMKilled, CPU over the limit gets throttled.
3. **How does a Service find its pods?** — Its label selector matches pod labels; endpoints are created for *ready* pods only.

**Gotchas**
- A liveness probe that checks dependencies (DB down → every pod restarts → cascading outage).
- CPU limits causing throttling and latency spikes.
- A selector/label mismatch leaves the Service with no endpoints.

**Scenario:** the DB had a 30-second blip and the whole app restarted in a loop. Why?

**Done when:** you can explain each field of your Deployment YAML.

**Resources:** [Kubernetes concepts](https://kubernetes.io/docs/concepts/) · [Configure probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

---

<a id="day-38"></a>
### Day 38 · DevOps · Helm and Kubernetes troubleshooting

**Time:** ~3 h

**Why it matters:** live troubleshooting is a common practical interview round for DevOps and platform roles.

**Learn**
- **Helm:** charts, values, templates, releases, upgrade/rollback, chart per service vs umbrella chart; Helm vs Kustomize.
- **Troubleshooting order:** `get` → `describe` → `logs` (`--previous`) → `events` → `exec`/`debug`.
- **Common states:** CrashLoopBackOff, ImagePullBackOff, Pending, OOMKilled, CreateContainerConfigError.

**Do**
- [ ] Helm charts for the .NET API, RAG API and agent service
- [ ] `helm upgrade` with a bad value, then `helm rollback`
- [ ] Drill: ask a friend (or a script) to break 5 things; fix each and log the commands in `docs/k8s-troubleshooting.md`

**Interview questions**
1. **A pod is in CrashLoopBackOff in production. What are your first five commands?** — `kubectl get pod -o wide`, `describe pod`, `logs --previous`, `get events --sort-by=.lastTimestamp`, then check config/secrets and recent deploys.
2. **What makes a pod Pending?** — Not enough CPU/memory for its requests, node selectors or taints, an unbound PVC or zone mismatch, quota limits.
3. **Helm or Kustomize?** — Helm for packaging, templating and releases; Kustomize for patching plain YAML per environment. Many teams use Helm charts with GitOps.

**Gotchas**
- Logs of the crashed container need `--previous`.
- ImagePullBackOff from a wrong tag or missing `AcrPull`.
- PVCs bound to one zone keep pods Pending in another zone.

**Scenario:** after a Helm upgrade, half the pods are healthy and half are in CreateContainerConfigError. What changed?

**Done when:** you've fixed 5 induced failures and written down how.

**Resources:** [Helm docs](https://helm.sh/docs/) · [Kubernetes debugging](https://kubernetes.io/docs/tasks/debug/)

---

<a id="day-39"></a>
### Day 39 · .NET + Design · Resilience patterns

**Time:** ~2 h

**Why it matters:** resilience trade-offs are a favourite senior and architect question, and .NET now has first-class support.

**Learn**
- **Patterns:** timeouts, retries with exponential backoff and jitter, circuit breaker, bulkhead, fallback.
- **In .NET:** `Microsoft.Extensions.Http.Resilience` (`AddStandardResilienceHandler`), built on Polly v8.
- **Retry storms:** how retries at every layer multiply load.
- **Graceful degradation:** serve partial results instead of failing.

**Do**
- [ ] Add the standard resilience handler to the .NET → FastAPI calls
- [ ] Inject failures (return 500s or add delays) and watch the circuit breaker open and recover

**Interview questions**
1. **What is a retry storm and how do you avoid it?** — Retries at many layers multiply traffic during an outage. Retry at one layer, add jitter, cap attempts, and use circuit breakers and retry budgets.
2. **What are the circuit breaker states?** — Closed (normal), open (fail fast), half-open (trial requests to test recovery).
3. **Where do timeouts belong?** — On every outbound call, shorter than the caller's own timeout, with an overall request deadline.

**Gotchas**
- Retrying non-idempotent operations.
- Timeouts longer than the upstream's timeout, so work continues after the caller gave up.
- A circuit breaker shared across unrelated endpoints.

**Scenario:** a slow downstream service made your whole API time out. Redesign the calls.

**Done when:** a downstream outage degrades your API gracefully instead of taking it down.

**Resources:** [.NET resilience](https://learn.microsoft.com/dotnet/core/resilience/) · [Retry pattern](https://learn.microsoft.com/azure/architecture/patterns/retry)

---

<a id="day-40"></a>
### Day 40 · Build + Defend · Support-ticket agent on AKS

**Time:** ~4 h

**Do**
- [ ] AKS via Terraform with workload identity; Helm charts for all three services
- [ ] Agent with approval step and persisted state; KEDA-scaled worker
- [ ] `docs/adr/005-agent-vs-workflow.md`
- [ ] Record answers to the three questions below

**Interview questions**
1. **A pod is in CrashLoopBackOff in production. What are your first five commands?** — Demo it live on your cluster.
2. **Traffic spikes 10× at month-end. How do pods, nodes and the database each scale?** — HPA/KEDA, cluster autoscaler with headroom, DB capacity (autoscale RU/vCore, read replicas, caching), plus a load test.
3. **When do you use an agent vs a fixed workflow, and what breaks agents in production?** — Use your graph as the example: deterministic edges plus one agentic step. Failure modes: tool errors, loops, context growth, prompt injection through emails.

**Gotchas**
- Emails are untrusted input: an email can contain instructions (indirect prompt injection). You'll harden this in Sprint 7.

**Done when:** an email submitted to the system ends as an approved ticket, and the full trace and approval are auditable.
