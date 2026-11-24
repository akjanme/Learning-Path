# Sprint 3 — Policy-document Q&A (Days 17–24)

**Scenario you build:** upload a PDF and it is automatically chunked, embedded and indexed. A RAG API then answers questions with page-level citations, and all of it is provisioned by Terraform.

[← Back to tracker](../TRACKER.md)

---

<a id="day-17"></a>
### Day 17 · Cloud · Choosing compute: App Service, Container Apps, Functions, AKS

**Time:** ~3 h

**Why it matters:** "which compute and why" is a standard architect question. A clear decision tree marks you as senior.

**Learn**
- **App Service:** plans, deployment slots, autoscale, VNet integration. Best for steady web APIs.
- **Container Apps:** KEDA-based scaling (including to zero), revisions and traffic splitting, Dapr. Microservices without running Kubernetes.
- **Functions:** triggers and bindings, Flex Consumption vs Premium vs Dedicated, cold starts, Durable Functions for orchestration.
- **AKS:** full Kubernetes control, for platform teams and complex workloads.
- **Decision factors:** ops burden, scaling model, networking needs, long-running work, cost at idle.

**Do**
- [ ] Deploy FastAPI to Container Apps with an HTTP scale rule
- [ ] Create a Function triggered by blob upload (Event Grid–based trigger)
- [ ] Deploy the .NET API to App Service and do a staging-slot swap

**Interview questions**
1. **Pick compute for (a) event-driven document processing, (b) a steady .NET API, (c) a 40-microservice platform.** — (a) Functions or Container Apps jobs, (b) App Service or Container Apps, (c) AKS, or Container Apps if the teams don't need Kubernetes. Justify each by ops effort and scaling.
2. **How do you reduce cold starts?** — Premium or Flex with always-ready instances, min replicas > 0 on Container Apps, smaller packages, avoiding heavy startup work.
3. **What does a slot swap actually swap?** — Content and most settings. Settings marked "deployment slot setting" stay with the slot. Warm-up happens before the swap.

**Gotchas**
- Consumption-plan Functions time out after 5 minutes by default (10 maximum), and HTTP requests are cut at about 230 seconds by the front end. Use async patterns for long jobs.
- Scale-to-zero means the first request pays the cold start.
- Functions that need VNet integration require the right plan (Flex Consumption or Premium).

**Scenario:** a team wants AKS for a single CRUD API. Talk them out of it, or into it, with numbers.

**Done when:** you have a one-page compute decision tree in `docs/compute-decision.md`.

**Resources:** [Choose an Azure compute service](https://learn.microsoft.com/azure/architecture/guide/technology-choices/compute-decision-tree) · [Container Apps docs](https://learn.microsoft.com/azure/container-apps/)

---

<a id="day-18"></a>
### Day 18 · Cloud · Messaging: Service Bus, Event Grid, Event Hubs

**Time:** ~3 h

**Why it matters:** choosing the wrong messaging service is a classic design mistake, and interviewers ask for this comparison constantly.

**Learn**
- **Service Bus:** queues, topics/subscriptions, peek-lock, sessions for ordering, dead-letter queue, duplicate detection, scheduled messages. For business commands and transactions.
- **Event Grid:** push-based event routing, filtering, retries and dead-lettering to blob, CloudEvents schema. For reacting to "something happened".
- **Event Hubs:** high-throughput streaming, partitions, consumer groups, retention, Kafka endpoint. For telemetry and streams.
- **Storage Queues:** simple and cheap, without the enterprise features.

**Do**
- [ ] Wire blob upload → Event Grid → Function → Service Bus queue → worker
- [ ] Send a poison message and watch it land in the dead-letter queue after max delivery count
- [ ] Fill a comparison table in `docs/messaging.md`

**Interview questions**
1. **Service Bus vs Event Grid vs Event Hubs, with a real example of each?** — Service Bus: "approve mandate" command. Event Grid: "blob created" notification. Event Hubs: clickstream or IoT telemetry.
2. **How do you guarantee ordering?** — Service Bus sessions (ordered per session ID) or Event Hubs partitions (ordered per partition key). Global ordering doesn't scale.
3. **Is delivery exactly once?** — In practice it's at-least-once. Design idempotent consumers; duplicate detection helps only within its time window.

**Gotchas**
- If processing takes longer than the lock duration, the message is redelivered and processed twice. Renew the lock or shorten the work.
- Dead-letter queues fill silently unless you alert on them.
- Event Hubs partition count is hard to change later, so plan it up front.

**Scenario:** customers receive the same notification three times. Find the cause.

**Done when:** you can explain why each arrow in your flow uses the service it does.

**Resources:** [Compare Azure messaging services](https://learn.microsoft.com/azure/service-bus-messaging/compare-messaging-services) · [Service Bus docs](https://learn.microsoft.com/azure/service-bus-messaging/)

---

<a id="day-19"></a>
### Day 19 · AI · Chunking, embeddings and Azure AI Search indexing

**Time:** ~3 h

**Why it matters:** retrieval quality decides RAG quality, and Azure AI Search is the most common enterprise RAG store on Azure.

**Learn**
- **Parsing:** PDFs, Word and tables; when you need layout/OCR (Document Intelligence) vs plain text extraction.
- **Chunking strategies:** fixed tokens with overlap, structure-aware (headings/sections), semantic. Store metadata on every chunk: source, page, section, ACL.
- **Embeddings:** model choice, dimensions, batch embedding, cost.
- **Azure AI Search index:** fields, vector fields (HNSW), filterable metadata, push indexing vs integrated vectorization.

**Do**
- [ ] Parse 5 policy PDFs and chunk by heading (~500 tokens, ~10–15% overlap)
- [ ] Embed the chunks and push them to an AI Search index with `content`, `vector`, `source`, `page`, `section`
- [ ] Run top-5 vector queries for 10 test questions and note the misses

**Interview questions**
1. **How do you choose chunk size?** — Small chunks give precise retrieval but lose context. Large chunks keep context but add noise and cost. Choose by document structure, then *measure* with an evaluation set.
2. **What happens when you change the embedding model?** — Re-embed and reindex everything, because vectors from different models aren't comparable. Run the new index side by side, then switch.
3. **Azure AI Search vs pgvector vs a dedicated vector DB?** — AI Search: hybrid search, semantic ranking, security filters, managed. pgvector: simple when Postgres is already the system of record. Dedicated DBs: very large scale or special features.

**Gotchas**
- Scanned PDFs and complex tables extract badly without OCR/layout models.
- Mixing embedding models or dimensions in one index.
- Not storing page numbers makes citations impossible later.

**Scenario:** users say the assistant "can't find" information that is clearly in a document. Debug retrieval.

**Done when:** at least 7 of 10 test questions return the right chunk in the top 5.

**Resources:** [Azure AI Search vector search](https://learn.microsoft.com/azure/search/vector-search-overview) · [RAG in Azure AI Search](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)

---

<a id="day-20"></a>
### Day 20 · AI · RAG v1 with citations and "I don't know"

**Time:** ~3 h

**Why it matters:** a grounded answer with citations is the baseline enterprises expect before anything goes live.

**Learn**
- **RAG flow:** query → retrieve → build context → generate with grounding instructions → cite.
- **Grounding prompt:** answer only from the provided context, cite sources, say "I don't know" when the context doesn't contain the answer.
- **Context budget:** how many chunks to include, ordering, de-duplication.
- **Follow-up questions:** rewrite the conversational query into a standalone query before retrieval.

**Do**
- [ ] `POST /ask` returns `answer` + `citations[]` (document, page, chunk ID)
- [ ] Return "I don't know" when retrieval scores are below a threshold
- [ ] Add query rewriting for follow-ups ("what about for contractors?")

**Interview questions**
1. **How do you reduce hallucinations in RAG?** — Better retrieval, strict grounding instructions, citations tied to chunk IDs, refusal when evidence is weak, and groundedness evaluation.
2. **How do you handle follow-up questions?** — Rewrite them into standalone queries using chat history, then retrieve. Don't just append the history to the search.
3. **How many chunks do you put in context?** — As few as give good answers. Tune k with evaluation; more chunks often lowers quality and raises cost.

**Gotchas**
- The model invents citations. Only allow citations to chunk IDs you actually passed in.
- Similarity scores aren't comparable across queries or indexes, so calibrate thresholds on your data.
- Stuffing 20 chunks "to be safe".

**Scenario:** legal says one wrong answer with a confident tone is unacceptable. What changes in your design?

**Done when:** every answer has valid citations, or explicitly says it doesn't know.

**Resources:** [LangChain RAG tutorial](https://python.langchain.com/docs/tutorials/rag/) · [RAG solution design guide](https://learn.microsoft.com/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide)

---

<a id="day-21"></a>
### Day 21 · DevOps · Terraform fundamentals

**Time:** ~3 h

**Why it matters:** Terraform is the de facto enterprise IaC tool, and its state model is what interviewers test.

**Learn**
- **Core language:** providers and version pinning, resources, data sources, variables, locals, outputs.
- **Lifecycle:** `init` → `plan` → `apply`; the dependency graph; replacement when a "force new" attribute changes.
- **State:** what it stores, why it's needed, and why it's sensitive.
- **Repetition:** `count` vs `for_each`, and why `for_each` with stable keys is safer.

**Do**
- [ ] Terraform for a resource group, storage account, Key Vault and AI Search
- [ ] Create 3 blob containers with `for_each`
- [ ] Change a "force new" attribute, read the plan and explain the replace

**Interview questions**
1. **What is Terraform state and why does it exist?** — The mapping between your config and real resource IDs, plus cached attributes. Terraform uses it to compute diffs. It holds secrets, so protect it.
2. **`count` vs `for_each`?** — `count` is indexed, so removing an item shifts the indexes and recreates resources. `for_each` is keyed and stable.
3. **The plan wants to destroy and recreate a database. Why, and what do you do?** — An attribute that forces replacement changed, or a resource address changed. Stop, check the diff, use `moved` blocks for renames, and add `prevent_destroy` on critical resources.

**Gotchas**
- State files contain secrets in plain text.
- Renaming a resource or a `for_each` key destroys and recreates it unless you add a `moved` block.
- Unpinned provider versions break builds on upgrade day.

**Scenario:** a junior engineer's apply is about to delete the production database. How should your setup have prevented it?

**Done when:** `terraform plan` is clean (no changes) right after an apply.

**Resources:** [Terraform Azure tutorials](https://developer.hashicorp.com/terraform/tutorials/azure-get-started) · [Terraform language docs](https://developer.hashicorp.com/terraform/language)

---

<a id="day-22"></a>
### Day 22 · DevOps · Terraform at team scale: backends, modules, drift, PR plans

**Time:** ~3 h

**Why it matters:** enterprises care about how Terraform works for many people safely, not about writing one resource.

**Learn**
- **Remote backend:** azurerm backend in a storage account, state locking via blob lease, separate state per environment and component.
- **Modules:** inputs and outputs, versioning (git tags or registry), keep modules small and composable.
- **Environments:** separate directories/state vs workspaces, and the trade-offs.
- **Drift and import:** `import` blocks, `terraform plan` for drift detection, `ignore_changes` used sparingly.
- **Quality gates:** `fmt`, `validate`, tflint, Checkov or Trivy config scanning, plan posted on the PR.

**Do**
- [ ] Move state to a remote backend
- [ ] Extract a `network` module and use it from a root config
- [ ] Create a resource in the portal, then bring it under Terraform with an `import` block
- [ ] GitHub workflow that runs `plan` on PRs and comments the output

**Interview questions**
1. **Someone changed a resource in the portal. What happens next, and what do you do?** — The next plan shows drift and will revert it. Decide whether the change was intended: codify it, or let Terraform revert it. Then prevent recurrences with RBAC and policy.
2. **Workspaces or separate folders for dev/test/prod?** — Separate folders and backends (or a wrapper tool) for strong isolation and different permissions. Workspaces suit identical, low-risk copies.
3. **How do you structure Terraform for 20 teams?** — Shared, versioned platform modules; each team owns its own root configs and state; PR plans; policy checks; least-privilege pipeline identities per environment.

**Gotchas**
- A stuck state lock after a crashed run. Use `force-unlock` only after confirming no apply is running.
- `lifecycle.ignore_changes` overused hides real drift.
- One giant state file means a huge blast radius and slow plans.

**Scenario:** two pipelines applied to the same state at the same time last night. What could happen, and what protects you?

**Done when:** a PR shows the Terraform plan as a comment.

**Resources:** [azurerm backend](https://developer.hashicorp.com/terraform/language/backend/azurerm) · [Terraform import blocks](https://developer.hashicorp.com/terraform/language/import)

---

<a id="day-23"></a>
### Day 23 · .NET + Design · Messaging patterns: outbox, idempotency, DLQs

**Time:** ~2 h

**Why it matters:** reliability with messaging is where senior .NET engineers stand out.

**Learn**
- **Dual-write problem:** writing to the DB and publishing an event can't be atomic without help.
- **Transactional outbox:** write the event to an outbox table in the same transaction, then publish it from a background process.
- **Idempotent consumer / inbox:** record processed message IDs; make handlers safe to repeat.
- **Operations:** dead-letter handling, poison messages, ordering keys, competing consumers.
- **Frameworks:** MassTransit / NServiceBus (awareness of what they give you).

**Do**
- [ ] Implement an outbox in the mandate service with EF Core plus a background publisher to Service Bus
- [ ] Implement an idempotent consumer using a processed-messages table

**Interview questions**
1. **What is the dual-write problem and how do you solve it?** — A DB commit followed by a failed publish (or the reverse) leaves inconsistent state. Fix it with the transactional outbox or change data capture.
2. **How do you guarantee customers never get duplicate emails?** — An idempotent consumer keyed on a business ID, deduplication storage, and at-least-once delivery accepted upstream.
3. **How do you preserve order per customer while scaling consumers?** — Partition or session by customer ID so one consumer handles one customer's messages at a time.

**Gotchas**
- Publishing the event before the DB transaction commits.
- Using a message ID that changes on resend as the idempotency key.
- One poison message blocking an entire session.

**Scenario:** after an outage, 30,000 messages are in the DLQ. What's your recovery plan?

**Done when:** killing the publisher mid-flight loses no events and creates no duplicates.

**Resources:** [Transactional outbox pattern](https://learn.microsoft.com/azure/architecture/databases/guide/transactional-outbox-cosmos) · [microservices.io patterns](https://microservices.io/patterns/)

---

<a id="day-24"></a>
### Day 24 · Build + Defend · Policy-document Q&A, end to end

**Time:** ~4 h

**Do**
- [ ] Everything in Terraform: storage, Event Grid, Function, Service Bus, AI Search, Container App, private endpoints
- [ ] Upload a PDF → indexed in under a minute → answerable via `/ask` with citations
- [ ] `docs/adr/003-event-grid-plus-service-bus.md`
- [ ] Record answers to the three questions below

**Interview questions**
1. **Service Bus vs Event Grid vs Event Hubs: how did you use them here, and why?** — Event Grid for the blob-created reaction, Service Bus for reliable processing with retries and DLQ. Event Hubs isn't needed at this volume.
2. **Someone changed a resource in the portal and Terraform now wants to destroy it. What do you do?** — Read the plan, decide whether to codify or revert the change, and use `import`/`moved` where needed. Then fix the access that allowed it.
3. **How did you choose chunk size and overlap, and how would you prove it's right?** — Structure-based chunking, then an evaluation set comparing 2–3 settings on hit rate and answer quality.

**Gotchas**
- Event Grid subscriptions to Functions created before the Function exists fail validation. Order the Terraform dependencies.
- Re-uploading the same file creates duplicate chunks unless you key chunk IDs on document + version.

**Done when:** `terraform destroy && terraform apply` rebuilds a working system with no manual steps.
