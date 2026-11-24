# Sprint 4 — Permission-aware RAG, shipped by a pipeline (Days 25–32)

**Scenario you build:** users only retrieve the documents their Entra groups allow. Retrieval is hybrid and reranked, quality is measured on an evaluation set, and everything ships through CI/CD with OIDC and no stored cloud secrets.

[← Back to tracker](../TRACKER.md)

---

<a id="day-25"></a>
### Day 25 · Cloud · Azure SQL and Cosmos DB

**Time:** ~3 h

**Why it matters:** choosing the right database and its key design is a top architect question and an expensive mistake to fix later.

**Learn**
- **Azure SQL:** vCore vs DTU, serverless (auto-pause), Hyperscale, zone redundancy, geo-replication and failover groups.
- **Entra-only auth** for SQL, with apps connecting via Managed Identity.
- **Cosmos DB:** partition key design, RU/s (manual vs autoscale), the five consistency levels (Session is the default), change feed.
- **Choosing:** relational integrity and complex queries → SQL. Massive scale, flexible schema, global distribution → Cosmos DB.

**Do**
- [ ] Azure SQL with Entra-only auth; the .NET API connects via Managed Identity
- [ ] Cosmos DB container for chat history with partition key `/userId`
- [ ] Run 3 queries and record their RU charge (point read vs in-partition vs cross-partition)

**Interview questions**
1. **Choose a partition key for chat history.** — `userId` (or `tenantId+userId`): high cardinality, matches the access pattern, spreads writes. Avoid date as the key because it creates hot partitions.
2. **SQL or Cosmos DB for mandates, and why?** — SQL: relational data, transactions across entities, reporting, strong consistency. Cosmos only if global scale or latency demands it.
3. **Explain Cosmos DB consistency levels.** — From Strong through Bounded Staleness, Session, Consistent Prefix, to Eventual. Session gives read-your-writes per client and is the usual default.

**Gotchas**
- Hot partitions throttle (429) even when total RU/s looks fine.
- A logical partition can't exceed 20 GB, so pick a key that keeps partitions bounded.
- Cross-partition queries are expensive.
- Serverless SQL auto-pause means a slow first query after idle.

**Scenario:** Cosmos DB costs doubled and users see 429s at peak. Diagnose it.

**Done when:** no connection string with a password exists anywhere in your solution.

**Resources:** [Cosmos DB partitioning](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview) · [Azure SQL docs](https://learn.microsoft.com/azure/azure-sql/)

---

<a id="day-26"></a>
### Day 26 · Cloud · Redis caching and data protection

**Time:** ~3 h

**Why it matters:** caching is the cheapest performance and cost win, and also an easy way to leak data.

**Learn**
- **Managed Redis on Azure:** check current Microsoft guidance, because Azure Managed Redis is the newer offering alongside Azure Cache for Redis.
- **Patterns:** cache-aside, TTLs, eviction policies, cache stampede protection.
- **.NET caching:** `IDistributedCache`, `HybridCache`.
- **Semantic cache for LLM calls:** reuse answers to semantically similar questions.
- **Data protection:** encryption at rest (platform vs customer-managed keys), TLS in transit, TDE on SQL.

**Do**
- [ ] Cache-aside for mandate lookups in .NET, and measure latency before and after
- [ ] Semantic cache for `/ask` (embedding similarity above a threshold), *scoped per permission set*
- [ ] Document what must never be cached

**Interview questions**
1. **How do you invalidate caches?** — TTL for tolerable staleness, explicit eviction on writes (events), versioned keys. Never rely on "we'll clear it manually".
2. **What is a cache stampede and how do you prevent it?** — Many requests miss at once and hit the DB. Prevent it with request coalescing/locks, early refresh and jittered TTLs.
3. **When is a semantic cache dangerous?** — When answers depend on the user's permissions or personal data: one user's cached answer could be served to another.

**Gotchas**
- A global cache of ACL-filtered answers leaks data across users.
- No TTL means stale data forever.
- Treating Redis as the system of record.

**Scenario:** after adding a cache, a customer sees another customer's mandate. What went wrong?

**Done when:** repeated questions are answered from the cache, but only for users with the same access.

**Resources:** [Caching guidance](https://learn.microsoft.com/azure/architecture/best-practices/caching) · [HybridCache in .NET](https://learn.microsoft.com/aspnet/core/performance/caching/hybrid)

---

<a id="day-27"></a>
### Day 27 · AI · Advanced retrieval: hybrid search, semantic ranking, query rewriting

**Time:** ~3 h

**Why it matters:** pure vector search fails on enterprise content full of codes, IDs and jargon. Hybrid retrieval is the production default.

**Learn**
- **Hybrid search:** keyword (BM25) + vector, merged with Reciprocal Rank Fusion.
- **Reranking:** Azure AI Search semantic ranker or cross-encoder rerankers. Better precision at the cost of latency.
- **Query techniques:** rewriting/expansion, multi-query, HyDE (awareness).
- **Filters:** metadata filters (department, document type, date) applied in the search, not after it.
- **Tuning:** top-k, reranked-k, score thresholds.

**Do**
- [ ] Build a 30-question evaluation set with expected source chunks
- [ ] Compare keyword, vector, hybrid, and hybrid + semantic ranker; record hit@5 and MRR in a table
- [ ] Pick a configuration and write down why

**Interview questions**
1. **Why does hybrid search beat vector-only for enterprise documents?** — Exact terms (policy numbers, product codes, names) are matched well by keyword search and poorly by embeddings. Hybrid gets both meaning and exact matches.
2. **What does a reranker do and what does it cost?** — It re-scores the top-N candidates with a stronger model for better precision, adding latency and per-query cost.
3. **How do you choose k?** — Empirically: plot quality against k on your evaluation set, and balance it against context cost and latency.

**Gotchas**
- An evaluation set that's too easy tells you nothing. Include paraphrases, typos and ID lookups.
- Reranking too many candidates adds latency for little gain.
- Applying filters after retrieval (post-filtering) starves results.

**Scenario:** search works for natural questions but fails for "what does clause 7.3.2 say?". Fix it.

**Done when:** your table shows a measurable improvement from the chosen configuration.

**Resources:** [Hybrid search in Azure AI Search](https://learn.microsoft.com/azure/search/hybrid-search-overview) · [Semantic ranker](https://learn.microsoft.com/azure/search/semantic-search-overview)

---

<a id="day-28"></a>
### Day 28 · AI · Security trimming and RAG evaluation

**Time:** ~3 h

**Why it matters:** "can users see documents they shouldn't?" is the first question every enterprise security review asks about RAG.

**Learn**
- **Document-level security:** store allowed group IDs on every chunk; filter at query time with the caller's group claims from their Entra token.
- **Platform support:** check the current Azure AI Search docs for document-level access control features versus filter-based trimming.
- **Retrieval metrics:** hit rate, recall@k, MRR.
- **Generation metrics:** groundedness/faithfulness, relevance, correctness.
- **Tools:** Microsoft Foundry (formerly Azure AI Foundry) evaluations, Ragas, LangSmith.

**Do**
- [ ] Add `allowed_groups` to the index and filter every query by the user's token groups
- [ ] Test: an HR-only document is invisible to a non-HR user, even with a direct question
- [ ] Evaluation script that outputs a table: retrieval hit rate, groundedness, relevance

**Interview questions**
1. **HR documents must only be visible to HR. How do you enforce that in RAG?** — Store ACLs per chunk at ingestion and filter at query time with the user's identity, inside the search query itself. Never rely on the prompt. Test it with negative cases.
2. **RAG answers are wrong 20% of the time. How do you tell whether retrieval or generation is at fault?** — Measure retrieval separately: was the right chunk in the context? If yes, it's a generation or prompt issue. If no, fix chunking, search or the query.
3. **How do you build a golden evaluation dataset?** — Real user questions plus SME-written answers and sources, edge cases and adversarial prompts, versioned and refreshed regularly.

**Gotchas**
- Entra tokens omit group claims for users in many groups (groups overage). Fetch them from Microsoft Graph or use app roles.
- ACLs that change after indexing need a sync process, or the access you enforce is stale.
- LLM-as-judge scores drift and are biased. Spot-check them by hand.

**Scenario:** an employee moved from HR to Sales this morning. When do they stop seeing HR documents, and how do you guarantee it?

**Done when:** your negative access tests pass and the evaluation table is committed.

**Resources:** [Security filters in AI Search](https://learn.microsoft.com/azure/search/search-security-trimming-for-azure-search) · [Ragas docs](https://docs.ragas.io/)

---

<a id="day-29"></a>
### Day 29 · DevOps · GitHub Actions with OIDC

**Time:** ~3 h

**Why it matters:** secretless CI/CD with environment approvals is the modern enterprise baseline.

**Learn**
- **Building blocks:** workflows, jobs, steps, runners (hosted vs self-hosted), matrix, caching, artifacts.
- **Environments:** protection rules, required reviewers, environment-scoped secrets and variables.
- **Reusable workflows** and composite actions for many repositories.
- **OIDC to Azure:** federated credentials on an app registration or managed identity, used by `azure/login`.
- **Hardening:** pin actions by SHA, least-privilege `permissions:`, care with `pull_request_target`.

**Do**
- [ ] CI for .NET and Python: restore/build/test/lint with caching
- [ ] Build the image, push it to ACR and deploy to Container Apps using OIDC, with no stored Azure secrets
- [ ] Add a `prod` environment with a required reviewer

**Interview questions**
1. **Why OIDC instead of stored service principal secrets?** — No long-lived secret to leak or rotate. Tokens are short-lived and scoped to a repo, branch or environment through the federation subject.
2. **How do you standardise pipelines across 30 repositories?** — Reusable workflows in a central repo, versioned, with inputs; required checks and rulesets at org level.
3. **How do you secure self-hosted runners?** — Ephemeral runners, isolated networks, no reuse across trust levels, and never running them for public-repo PRs.

**Gotchas**
- The federated credential subject must match exactly (branch vs environment vs PR), or login fails with a vague error.
- Third-party actions pinned by tag can be repointed. Pin by commit SHA.
- Secrets aren't available to PRs from forks, by design.

**Scenario:** a compromised third-party action exfiltrated tokens across your org. What limits the damage next time?

**Done when:** a merge to main deploys automatically, and prod waits for approval.

**Resources:** [GitHub Actions docs](https://docs.github.com/actions) · [OIDC with Azure](https://docs.github.com/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-azure)

---

<a id="day-30"></a>
### Day 30 · DevOps · Azure DevOps pipelines and CI/CD design at scale

**Time:** ~3 h

**Why it matters:** many enterprises (especially Microsoft shops and banks) run Azure DevOps. Pipeline *design* is a common senior question.

**Learn**
- **YAML pipelines:** stages, jobs, deployment jobs, templates (`extends` for enforced standards).
- **Variable groups** linked to Key Vault; service connections using workload identity federation.
- **Environments:** checks and approvals, exclusive locks, branch control.
- **Promotion:** build once, promote the same artifact through dev → test → prod.
- **Deployment strategies:** rolling, blue-green, canary, and rollback.

**Do**
- [ ] Recreate your pipeline in Azure DevOps with a shared template repo
- [ ] Multi-stage dev → test → prod with approval on prod
- [ ] Workload-identity-federation service connection (no secret)

**Interview questions**
1. **Design CI/CD for 30 microservices owned by 6 teams.** — Per-service pipelines from shared templates; build once, sign and scan; promote by environment with gates; trunk-based development; feature flags; GitOps for deploy; DORA metrics.
2. **Why promote one artifact instead of rebuilding per environment?** — So what you tested is exactly what you deploy. Rebuilding introduces drift.
3. **What is your rollback strategy?** — Redeploy the previous artifact (or revert in GitOps), with backward-compatible DB migrations (expand/contract) so rollback is safe.

**Gotchas**
- Rebuilding per environment produces different artifacts.
- A service connection with Owner on the subscription.
- Destructive DB migrations make "rollback" impossible.

**Scenario:** a deploy broke prod, and the previous version can't run against the migrated database. How do you avoid this in future?

**Done when:** the same artifact version is visible in dev, test and prod.

**Resources:** [Azure Pipelines docs](https://learn.microsoft.com/azure/devops/pipelines/) · [Pipeline templates](https://learn.microsoft.com/azure/devops/pipelines/process/templates)

---

<a id="day-31"></a>
### Day 31 · .NET + Design · Caching, database choice, partitioning

**Time:** ~2 h

**Why it matters:** these are the deep-dive questions in almost every system design round.

**Learn**
- **Caching layers:** client, CDN, application, database. Write-through, write-behind and cache-aside.
- **Database choice:** SQL vs document vs key-value vs wide-column; read replicas.
- **Partitioning/sharding:** hash vs range vs directory; consistent hashing; resharding pain.
- **Consistency:** replica lag, read-your-writes.

**Do**
- [ ] 45-minute drill: design a product catalogue (or news feed) for 10M users with caching and sharding (`design/catalogue.md`)

**Interview questions**
1. **How do you choose a shard key?** — High cardinality, even distribution, matches the main access pattern, avoids cross-shard queries for hot paths.
2. **Read replica or cache: which and when?** — A cache for hot, tolerant-of-staleness reads with low latency. Replicas for offloading complex read queries. Both lag.
3. **How do you provide read-your-writes with replicas?** — Read from the primary for a short window after the user's write, use session tokens, or route by user.

**Gotchas**
- Hot keys (a celebrity account, a flash-sale product).
- Cross-shard joins and transactions.
- Forgetting replica lag in user-facing flows.

**Scenario:** one tenant is 40% of all traffic and slows everyone. Redesign.

**Done when:** your design shows numbers (QPS, storage, cache hit rate), not just boxes.

**Resources:** [Data partitioning guidance](https://learn.microsoft.com/azure/architecture/best-practices/data-partitioning) · [System Design Primer](https://github.com/donnemartin/system-design-primer)

---

<a id="day-32"></a>
### Day 32 · Build + Defend · Permission-aware RAG, shipped by pipeline

**Time:** ~4 h

**Do**
- [ ] Pipeline: build → test → scan → Terraform plan/apply → deploy, using OIDC
- [ ] Hybrid + semantic retrieval with ACL filtering; evaluation results in the README
- [ ] Conversation history in Cosmos DB, safe cache in Redis
- [ ] `docs/adr/004-security-trimming-approach.md`
- [ ] Record answers to the three questions below

**Interview questions**
1. **HR documents must only be visible to HR. Show how your system enforces it.** — Walk through ingestion ACLs, the query filter from token claims, negative tests, and ACL sync on group changes.
2. **RAG answers are wrong 20% of the time. How do you diagnose it?** — Split retrieval and generation metrics, inspect failures by category, fix the biggest bucket first, and re-run evaluation in CI.
3. **Design CI/CD for 30 microservices and 6 teams.** — Use your own pipeline as the worked example, then generalise with templates and governance.

**Gotchas**
- Running evaluation against production data in CI. Use a fixed test index.
- The pipeline identity having more rights than the app needs.

**Done when:** a PR that changes retrieval settings shows the evaluation score in the PR checks.
