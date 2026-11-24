# Sprint 2 — Private internal AI assistant (Days 9–16)

**Scenario you build:** an internal AI assistant where every PaaS service sits behind a private endpoint. The only public entry point is an Application Gateway with WAF, and the LLM returns validated, machine-readable output.

[← Back to tracker](../TRACKER.md)

---

<a id="day-9"></a>
### Day 9 · Cloud · Azure networking: VNets, NSGs, hub-spoke

**Time:** ~3 h

**Why it matters:** networking is where most enterprise cloud projects stall, and the most common hands-on troubleshooting interview topic.

**Learn**
- **VNets and subnets:** address planning with non-overlapping CIDRs. Azure reserves 5 IPs in every subnet.
- **NSGs:** stateful rules, priorities, default rules, service tags, application security groups.
- **Routing:** system routes, user-defined routes (UDRs), forcing `0.0.0.0/0` through Azure Firewall or an NVA.
- **Hub-spoke:** peering is non-transitive; shared services (firewall, DNS, VPN/ExpressRoute) live in the hub; Virtual WAN is the managed alternative.
- **Outbound access:** plan explicit outbound (NAT Gateway or firewall). Default outbound access is being retired for new VNets.

**Do**
- [ ] Build a hub VNet and two spoke VNets, peered to the hub (Terraform or CLI, whichever is faster for now)
- [ ] Add NSGs that allow only app-tier → data-tier traffic on the needed port
- [ ] Test connectivity with Network Watcher *connection troubleshoot* or two small VMs

**Interview questions**
1. **Is VNet peering transitive? How do two spokes talk?** — No. Route spoke-to-spoke traffic through a firewall or NVA in the hub using UDRs, use Virtual WAN, or peer the spokes directly if policy allows.
2. **NSG vs Azure Firewall?** — An NSG is a distributed L3/L4 stateful filter on a subnet or NIC. Azure Firewall is a central L3–L7 service with FQDN filtering, threat intelligence, TLS inspection (Premium) and central logging. Enterprises use both.
3. **How do you plan IP addressing for 50 spokes plus on-premises?** — Get a non-overlapping range from network/IPAM up front. Size spokes for growth (especially AKS) and keep a summary range per region.

**Gotchas**
- Overlapping CIDRs block peering and VPN connections, and fixing them later means rebuilding.
- Some subnet names are mandatory: `AzureFirewallSubnet`, `GatewaySubnet`, `AzureBastionSubnet`.
- A UDR sending `0.0.0.0/0` to a firewall with missing rules silently breaks egress (AKS node bootstrap, package installs).
- Classic Azure CNI gives every pod a VNet IP, which exhausts subnets quickly.

**Scenario:** two spokes are both peered to the hub but can't reach each other. Walk through the diagnosis.

**Done when:** you can draw the packet path between two spokes and name every hop.

**Resources:** [Hub-spoke topology (Architecture Center)](https://learn.microsoft.com/azure/architecture/networking/architecture/hub-spoke) · [Virtual network docs](https://learn.microsoft.com/azure/virtual-network/)

---

<a id="day-10"></a>
### Day 10 · Cloud · Private Endpoints, private DNS, App Gateway, Front Door

**Time:** ~3 h

**Why it matters:** "no public endpoints" is the default rule in banks and regulated companies, and DNS is where it breaks.

**Learn**
- **Private Endpoint vs Service Endpoint:** a private IP in your VNet for one resource, vs your subnet's traffic reaching the service's public endpoint over the Azure backbone.
- **Private DNS:** `privatelink.*` zones, VNet links, how name resolution flips to the private IP, and DNS Private Resolver for on-premises clients.
- **Public network access:** disable it on the resource after the private endpoint works.
- **Entry points:** App Gateway (regional L7 + WAF), Front Door (global L7, CDN, WAF), Load Balancer (L4), Traffic Manager (DNS-based).

**Do**
- [ ] Create private endpoints for Key Vault and Azure OpenAI, plus private DNS zones linked to the spoke
- [ ] Disable public network access on both
- [ ] From inside the VNet, `nslookup` both FQDNs and confirm they resolve to private IPs
- [ ] Put App Gateway (WAF v2, Prevention mode) in front of the API

**Interview questions**
1. **Private endpoint vs service endpoint?** — A private endpoint gives the resource a private IP and works from on-premises and peered VNets. A service endpoint keeps the public IP but restricts access to the subnet. Enterprises standardise on private endpoints.
2. **An app can't reach a resource over its private endpoint. How do you troubleshoot?** — DNS first: does the FQDN resolve to the private IP *from the caller's VNet*? Then check the private DNS zone link, custom DNS forwarding to Azure DNS (168.63.129.16), NSG/UDR on the path, and public access settings.
3. **Front Door vs App Gateway: when do you use both?** — Front Door for global entry, failover and edge WAF. App Gateway for regional L7 routing into private backends. Front Door → Private Link → backend is the common pattern.

**Gotchas**
- A private DNS zone that isn't linked to the client's VNet means the name still resolves to the public IP.
- On-premises clients need conditional forwarders to a DNS Private Resolver.
- Using the `privatelink` FQDN in a connection string breaks TLS validation. Keep the normal FQDN.
- WAF in Detection mode logs but blocks nothing.

**Scenario:** after a private endpoint is enabled on Storage, an Azure Function can no longer connect. What happened?

**Done when:** the only public IP in your environment belongs to App Gateway.

**Resources:** [Private Endpoint DNS](https://learn.microsoft.com/azure/private-link/private-endpoint-dns) · [Application Gateway docs](https://learn.microsoft.com/azure/application-gateway/)

---

<a id="day-11"></a>
### Day 11 · AI · LLM fundamentals that interviewers probe

**Time:** ~3 h

**Why it matters:** you need to explain *why* LLM apps behave as they do, not just call an API.

**Learn**
- **How generation works:** next-token prediction, attention (intuition only), and why fluent answers can be wrong (hallucination).
- **Tokens and context:** tokenization, context windows, input vs output pricing, and the fact that models use long contexts unevenly ("lost in the middle").
- **Sampling:** temperature, top_p, seed. Even temperature 0 isn't fully deterministic.
- **Embeddings:** text → vector; cosine similarity; dimensions vs cost.
- **Model choice:** large vs small, reasoning models, open-weight models; trade quality against latency and cost.

**Do**
- [ ] Notebook: count tokens for 5 of your documents (English and one non-English) with `tiktoken`
- [ ] Run the same prompt 5× at temperature 0 and 1 and compare
- [ ] Embed 10 sentences and print a similarity matrix
- [ ] One-table comparison of 3 models: context window, price per 1M input/output tokens, typical latency

**Interview questions**
1. **Why do LLMs hallucinate, and how do you reduce it in an enterprise app?** — They generate plausible tokens, not verified facts. Reduce it with grounding (RAG), instructions to answer only from context, citations, refusing when context is missing, constrained output, and evaluation.
2. **What drives the cost and latency of an LLM call?** — Token counts, model size, output length and concurrency or quota. Mitigate with smaller models for simple steps, caching, shorter prompts and streaming.
3. **When would you choose a small model over a frontier model?** — For classification, routing, extraction and high-volume, latency-sensitive tasks, once evaluation shows the quality is good enough.

**Gotchas**
- Non-English text (for example Arabic) often uses noticeably more tokens, so cost and context differ by language.
- A bigger context window is not free accuracy. Too much context lowers quality and raises cost.
- Model versions are retired on a schedule. Pin versions and plan upgrades with evaluations.

**Scenario:** a business user complains that the same question gets different answers. Explain why and what you'd change.

**Done when:** you can explain tokens, temperature and embeddings to a non-technical manager in 2 minutes.

**Resources:** [DeepLearning.AI short courses](https://www.deeplearning.ai/short-courses/) · [Hugging Face LLM course](https://huggingface.co/learn)

---

<a id="day-12"></a>
### Day 12 · AI · Prompting, structured output and function calling

**Time:** ~3 h

**Why it matters:** enterprise LLM features feed other systems, so output must be reliable and actions must be safe.

**Learn**
- **Prompt structure:** system message, task instructions, context, examples (few-shot), clear delimiters.
- **Structured outputs:** JSON-schema-constrained output, validated again with Pydantic, with a bounded retry on failure.
- **Function/tool calling:** the model *proposes* a call; your code checks it, executes it and returns the result.
- **Prompts as code:** templates in files, versioned, with tests.

**Do**
- [ ] `POST /extract` turns free-text mandate requests into a Pydantic model via structured outputs
- [ ] Add one tool, `get_account(account_id)`, calling a stub .NET endpoint
- [ ] 10 test cases, including malformed and adversarial inputs

**Interview questions**
1. **How do you make LLM output reliably machine-parseable?** — Schema-constrained structured outputs, validation at the boundary, a bounded retry with the error message, and a safe fallback path.
2. **Who executes a function call, the model or your application, and why does it matter?** — Your application. Authorization, input validation and side effects must be enforced in your code with the *user's* permissions, never trusted to the model.
3. **How do you test prompts?** — Keep a fixed test set with expected properties, run it in CI on every prompt or model change, and track scores over time.

**Gotchas**
- Plain "JSON mode" guarantees valid JSON, not your schema. Use schema-based structured outputs.
- Tool descriptions are prompts too: vague descriptions mean wrong tool choices.
- Too many tools in one call degrades tool selection.
- Editing a prompt without running tests is an untested production change.

**Scenario:** a downstream system crashes on 2% of requests because the LLM's JSON is malformed. Fix it.

**Done when:** 10/10 test cases return schema-valid output or a handled error.

**Resources:** [Azure OpenAI structured outputs](https://learn.microsoft.com/azure/ai-services/openai/how-to/structured-outputs) · [OpenAI function calling guide](https://platform.openai.com/docs/guides/function-calling)

---

<a id="day-13"></a>
### Day 13 · DevOps · Production-grade images, ACR and scanning

**Time:** ~3 h

**Why it matters:** container security findings are one of the most common blockers for go-live in enterprises.

**Learn**
- **Minimal base images:** chiseled .NET images, distroless, `python:*-slim`; non-root users; read-only filesystem.
- **Tagging:** immutable tags (git SHA) and digests; never deploy `latest`.
- **Azure Container Registry:** tiers, geo-replication, private endpoint, `AcrPull` via Managed Identity, admin user disabled.
- **Scanning:** Trivy for OS and library CVEs; fix base images first; rescan images already in the registry.

**Do**
- [ ] Push both images to ACR tagged with the git SHA
- [ ] Run Trivy, failing on HIGH/CRITICAL
- [ ] Switch .NET to a chiseled base image and compare CVE count and size

**Interview questions**
1. **How do you keep container images secure over time?** — Minimal bases, scanning in CI *and* in the registry, scheduled rebuilds to pick up base-image patches, and an SLA for fixing critical CVEs.
2. **Tag or digest: which do you deploy?** — A digest is immutable. Tags can move. Use SHA tags for humans and pin by digest for strict environments.
3. **How does a cluster pull from a private registry without passwords?** — The kubelet/managed identity is granted `AcrPull` (AKS attach-ACR), with the registry reached over a private endpoint.

**Gotchas**
- Scanning only at build time: new CVEs appear against images that are already running.
- Distroless/chiseled images have no shell. Debug with ephemeral debug containers.
- Building on an ARM laptop produces arm64 images that fail on amd64 nodes with `exec format error`. Use `--platform`.

**Scenario:** Security reports 40 critical CVEs in production images. What's your plan for today and for next month?

**Done when:** your pipeline (or script) blocks an image with a critical CVE.

**Resources:** [Trivy docs](https://trivy.dev/) · [ACR docs](https://learn.microsoft.com/azure/container-registry/)

---

<a id="day-14"></a>
### Day 14 · DevOps · Bash, Azure CLI automation and network troubleshooting

**Time:** ~3 h

**Why it matters:** live troubleshooting rounds test whether you can find problems from a terminal quickly.

**Learn**
- **Bash essentials:** quoting, `set -euo pipefail`, functions, loops, exit codes, `jq`.
- **Azure CLI:** `--query` (JMESPath), `-o tsv`, logging in with a managed identity or federated identity in pipelines.
- **Idempotent scripts:** check before create; safe to re-run.
- **Troubleshooting toolkit:** `curl -v`, `openssl s_client`, `dig`, `nc`, `traceroute`, basic `tcpdump`.

**Do**
- [ ] Script: list resources missing a `CostCenter` tag and output CSV
- [ ] Script: for a list of endpoints, check DNS resolution, TCP connect and TLS certificate expiry
- [ ] Run `shellcheck` on both scripts and fix the warnings

**Interview questions**
1. **What does `set -euo pipefail` do?** — Exit on error, error on unset variables, and fail a pipeline if any command in it fails.
2. **"Connection timed out" vs "connection refused"?** — Timed out: packets dropped (NSG, firewall, routing). Refused: the host is reachable but nothing is listening on that port.
3. **How do you debug a TLS handshake failure?** — `openssl s_client -connect host:443 -servername host`: check the certificate chain, SNI, protocol versions, expiry, and whether a proxy intercepts TLS.

**Gotchas**
- Unquoted variables break on spaces and globbing.
- Scripts that work locally fail in pipelines: different shell (`sh` vs `bash`), missing login, different working directory.
- Hard-coded subscription IDs and resource names.

**Scenario:** users see intermittent 502s from App Gateway. What do you check, in order?

**Done when:** both scripts are idempotent and shellcheck-clean.

**Resources:** [Azure CLI query docs](https://learn.microsoft.com/cli/azure/query-azure-cli) · [ShellCheck](https://www.shellcheck.net/)

---

<a id="day-15"></a>
### Day 15 · .NET + Design · API design, gateways, load balancing, rate limiting

**Time:** ~2 h

**Why it matters:** API design shows up in every system design round and in every architect interview.

**Learn**
- **REST design:** resources, status codes, pagination, versioning, idempotency keys.
- **Choosing a style:** REST vs gRPC vs async messaging.
- **API gateway duties:** auth, rate limiting, routing, transformation, observability.
- **Load balancing:** L4 vs L7, algorithms, health checks, why sticky sessions hurt.
- **Rate limiting:** token bucket, sliding window, and the ASP.NET Core rate-limiting middleware.

**Do**
- [ ] Add API versioning and an `Idempotency-Key` header to the mandate `POST`
- [ ] Add ASP.NET Core rate limiting per client
- [ ] 45-minute drill: design a distributed rate limiter for a public API (`design/rate-limiter.md`)

**Interview questions**
1. **How do you make a POST idempotent?** — The client sends an idempotency key. The server stores key → result atomically and returns the stored result on retries.
2. **Design a distributed rate limiter.** — Token bucket per client in Redis with atomic Lua or `INCR` + TTL. Decide fail-open vs fail-closed, return 429 with `Retry-After`, and consider local plus global limits.
3. **How do you ship a breaking API change with 40 consumers?** — A new version alongside the old, a deprecation policy and headers, usage telemetry per consumer, and a migration window before you remove the old one.

**Gotchas**
- An in-memory rate limiter is per instance, not global, once you scale out.
- Sticky sessions hide state and break when instances scale or fail.
- Retries without idempotency create duplicate payments.

**Scenario:** a partner's retry bug sends 50× normal traffic at the mandate API. Protect the system and the other partners.

**Done when:** retrying the same `POST` with the same key returns the same result and creates no duplicate.

**Resources:** [ASP.NET Core rate limiting](https://learn.microsoft.com/aspnet/core/performance/rate-limit) · [Azure API design guidance](https://learn.microsoft.com/azure/architecture/best-practices/api-design)

---

<a id="day-16"></a>
### Day 16 · Build + Defend · Private internal AI assistant

**Time:** ~4 h

**Do**
- [ ] All PaaS services (Key Vault, Azure OpenAI, ACR, storage) behind private endpoints, with public access disabled
- [ ] App Gateway WAF as the only public entry; FastAPI `/chat` returns schema-validated output
- [ ] Images from ACR, scanned, non-root
- [ ] `docs/adr/002-front-door-vs-app-gateway.md`
- [ ] Network diagram showing each request hop and DNS resolution
- [ ] Record answers to the three questions below

**Interview questions**
1. **The app can't reach Azure OpenAI over a private endpoint. Troubleshoot it.** — DNS resolution from the caller, zone link, custom DNS forwarders, NSG/UDR, public access flag, identity and RBAC, then application logs. Show the commands you'd run.
2. **Front Door vs App Gateway vs API Management: where does each go?** — Front Door: global edge. App Gateway: regional L7/WAF into the VNet. APIM: API product layer for auth, quotas, transformation and AI policies. They are often chained.
3. **How do you make LLM output reliable enough for downstream systems?** — Schema-constrained output, validation, retries, fallbacks, tests in CI, and monitoring the parse-failure rate.

**Gotchas**
- Azure OpenAI private endpoint plus a custom DNS server without forwarding is the most common failure in this build.
- App Gateway health probes failing on `/` when your app only serves `/health` gives 502s.

**Done when:** `nmap` or an external `curl` reaches nothing except App Gateway, and the assistant still works.
